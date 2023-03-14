#!/usr/bin/env cs_python
# pylint: disable=line-too-long

""" Compute A*B using a 2-by-2 PE rectangle

   The 2-by-2 rectangle is surrounded by a halo of size 1.
   The halo is used to route the input and output data between the host and the device.
   It does not impact the layout index of the kernel code.
   For example, the kernel has 2-by-2 PEs, with the index P0.0, P1.0, P0.1, P1.1
   in the layout/routing configuration.
   The compiler generates ELFs out_0_0.elf, out_0_1.elf, out_1_0.elf and out_1_1.elf.
   However the user needs global coordinate (including halo) for debugging, for example
   P0.0 of the kernel is P1.1 when the user calls sdk_debug_shell to dump the trace or
   landing log.

   Each PE computes its local A*B and does a row reduction, so last column has the result A*B = C_final.

   To simplify the example, the dimensions N and K are assumed even.
   A functions spmm_csc_f32 is used to compute C_temp=A*B using the CSC grid format.
   This function is imported as a module via spmm_csc.csl.
   The arrays A_val, A_row_idx, A_col_ptr, B, C_temp and C_final are passed into the function as pointers.

   The matrix B is distributed into columns. The first row receives B from the fabric,
   then broadcasts B into other rows.

   P1.0 and P1.1 compute the reduction C_final which is sent out..

   One can use the following command to check the landing log of P0.0,
    sdk_debug_shell wavelet-trace --artifact_dir . --x 1 --y 1 trace

"""


import os
import argparse
from pathlib import Path
from typing import Optional
import shutil
import subprocess
import numpy as np

from cerebras.sdk.runtime import runtime_utils # pylint: disable=no-name-in-module
from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime # pylint: disable=no-name-in-module

FILE_PATH = os.path.realpath(__file__)
RESIDUAL_DIR = os.path.dirname(FILE_PATH)
BENCHMARKS_DIR = os.path.dirname(RESIDUAL_DIR)
CSL_DIR = os.path.dirname(BENCHMARKS_DIR)
CSLC = os.path.join(CSL_DIR, "build") + "/bin/cslc"


def cast_uint32(x):
  if isinstance(x, (np.float16, np.int16, np.uint16)):
    z = x.view(np.uint16)
    return np.uint32(z)
  if isinstance(x, (np.float32, np.int32, np.uint32)):
    return x.view(np.uint32)
  if isinstance(x, int):
    return np.uint32(x)

  raise RuntimeError(f"type of x {type(x)} is not supported")



def parse_args():
  """ parse the command line """

  parser = argparse.ArgumentParser(description="residual parameters.")
  parser.add_argument("-N", type=int,
                      help="number of rows of the A and C_temp/C_final")
  parser.add_argument("-K", type=int,
                      help="number of columns of the  A and number of rows of B")
  parser.add_argument("-M", type=int,
                      help="number of columns of the matrix B and C.")
  parser.add_argument("-A_prefix", type=str,
                      help="prefix of all three grid csc files")
  parser.add_argument(
      "--cslc",
      required=False,
      default=CSLC,
      help=f"The path to the csl compiler. Defaults to '{CSLC}'",
  )
  parser.add_argument(
      "-c", "--compile", action="store_true", help="Compile the code."
  )
  parser.add_argument(
      "--name",
      required=False,
      default="out",
      help="prefix of ELF files",
  )
  parser.add_argument("--cmaddr", help="IP:port for CS system")
  parser.add_argument(
      "--fabric-dims",
      help="Fabric dimension, i.e. <W>,<H>")

  parser.add_argument(
      "--width-west-buf",
      default=0, type=int,
      help="width of west buffer")
  parser.add_argument(
      "--width-east-buf",
      default=0, type=int,
      help="width of east buffer")
  parser.add_argument(
      "--n_channels",
      default=1, type=int,
      help="Number of memcpy \"channels\" (LVDS/streamers for both input and output)  to use \
            when memcpy support is compiled with this program. If this argument is not present, \
            or is 0, then the previous single-LVDS version is compiled.")
  parser.add_argument(
      "--arch",
      help="wse1 or wse2. Default is wse1 when not supplied.")

  args = parser.parse_args()

  return args


def csl_compile(
    cslc: str,
    width: int,
    height: int,
    file_config: str,
    elf_dir: str,
    fabric_width: int,
    fabric_height: int,
    core_fabric_offset_x: int,
    core_fabric_offset_y: int,
    compile_flag: bool,
    arch: Optional[str],
    LAUNCH: int,
    A_val_len: int,
    A_rowidx_len: int,
    A_colptr_len: int,
    M: int,
    Nt: int,
    Kt: int,
    n_channels: int,
    width_west_buf: int,
    width_east_buf: int
    ):
  """Generate ELFs for the layout, one ELF per PE"""

  comp_dir = elf_dir

  if compile_flag:
    args = []
    args.append(cslc) # command
    args.append(file_config) # file
    args.append(f"--fabric-dims={fabric_width},{fabric_height}") # options
    args.append(f"--fabric-offsets={core_fabric_offset_x},{core_fabric_offset_y}") # options
    args.append(f"--params=width:{width},height:{height}") # options
    args.append(f"--params=Nt:{Nt}, Kt:{Kt}, M:{M}, A_val_len:{A_val_len}, A_rowidx_len:{A_rowidx_len}, A_colptr_len:{A_colptr_len}") # options

    args.append(f"--params=LAUNCH_ID:{LAUNCH}") # options

    args.append(f"-o={comp_dir}")
    if arch is not None:
      args.append(f"--arch={arch}")
    args.append("--memcpy")
    args.append(f"--channels={n_channels}")
    args.append(f"--width-west-buf={width_west_buf}")
    args.append(f"--width-east-buf={width_east_buf}")
    print(f"subprocess.check_call(args = {args}")
    subprocess.check_call(args)
  else:
    print("[csl_compile] use pre-compile ELFs")



def main():
  """Main method to run the code."""

  args = parse_args()

#  if not, must redo the routing
  width = 2
  height = 2

  if args.N is not None:
    N = args.N
  else:
    N = 6

  if args.K is not None:
    K = args.K
  else:
    K = 4

  if args.M is not None:
    M = args.M
  else:
    M = 8

  if args.A_prefix is not None:
    A_prefix = args.A_prefix
  else:
    A_prefix = "test"

  Nt = N // height
  Kt= K // width

  assert N == (Nt*height), "N must be multiple of Nt"
  assert K == (Kt*width), "K must be multiple of Kt"

  Nt = int(Nt)
  Kt = int(Kt)

  print(f"N = {N}, K = {K}, M = {M}, width = {width}, height = {height}")

  # prepare host data and reference solution
  file_dir = "test_vectors/"

  A_val_file = file_dir+A_prefix+"_val_pad.csv"
  A_colptr_file = file_dir+A_prefix+"_col_ptr_pad.csv"
  A_rowidx_file = file_dir+A_prefix+"_row_idx_pad.csv"

  # Read in
  A_val = np.genfromtxt(A_val_file, delimiter=",", dtype=np.float32)
  print(A_val)
  A_row_idx = np.genfromtxt(A_rowidx_file, delimiter=",", dtype=np.int32)
  A_col_ptr = np.genfromtxt(A_colptr_file, delimiter=",", dtype=np.int32)

  # Get lengths
  A_val_len = A_val.shape[1]
  A_rowidx_len = A_row_idx.shape[1]
  A_colptr_len = A_col_ptr.shape[1]

  np.random.seed(2)
  B = np.arange(K*M).reshape(K, M).astype(np.float32) + 100

  # TODO: implement CSC matmul
  C_ref = B
  # TODO: print C_reference
  print(f"B = {C_ref}")

  # prepare the simulation

  # core dump after execution is complete
  # layout of a rectangle
  code_csl = "layout.csl"

  # text file containing the simulator logs
  sim_log = os.path.join(args.name, "sim.log")

  n_channels = args.n_channels
  width_west_buf = args.width_west_buf
  width_east_buf = args.width_east_buf
  print(f"n_channels = {n_channels}")
  print(f"width_west_buf = {width_west_buf}, width_east_buf = {width_east_buf}")

  fabric_offset_x = 1
  fabric_offset_y = 1
  fabric_width = 0
  fabric_height = 0
  if args.fabric_dims:
    w_str, h_str = args.fabric_dims.split(",")
    fabric_width = int(w_str)
    fabric_height = int(h_str)

  if fabric_width == 0 or fabric_height == 0:
    fabric_width = fabric_offset_x + 3 + width + 2 + 1 + width_west_buf + width_east_buf
    fabric_height = fabric_offset_y + height + 1

  core_fabric_offset_x = fabric_offset_x + 3 + width_west_buf
  core_fabric_offset_y = fabric_offset_y

  print(f"fabric_width = {fabric_width}, fabric_height = {fabric_height}")
  print(f"core_fabric_offset_x = {core_fabric_offset_x}, core_fabric_offset_y = {core_fabric_offset_y}")

  LAUNCH = 4

  # compile csl files and generate compilation ELFs
  csl_compile(
      args.cslc,
      width,
      height,
      code_csl,
      args.name,
      fabric_width,
      fabric_height,
      core_fabric_offset_x,
      core_fabric_offset_y,
      args.compile,
      args.arch,
      LAUNCH,
      A_val_len,
      A_rowidx_len,
      A_colptr_len,
      M,
      Nt,
      Kt,
      n_channels,
      width_west_buf,
      width_east_buf)
  if args.compile:
    print("COMPILE ONLY: EXIT")
    return

  simulator = SdkRuntime(args.name, cmaddr=args.cmaddr)

  symbol_A_val = simulator.get_id("A_val")
  symbol_A_row_idx = simulator.get_id("A_row_idx")
  symbol_A_col_ptr = simulator.get_id("A_col_ptr")
  symbol_B = simulator.get_id("B")
  symbol_C_temp = simulator.get_id("C_temp")
  symbol_C_final = simulator.get_id("C_final")

  print(f"symbol_A_val = {symbol_A_val}")
  print(f"symbol_A_row_idx = {symbol_A_row_idx}")
  print(f"symbol_A_col_ptr = {symbol_A_col_ptr}")
  print(f"symbol_x = {symbol_B}")
  print(f"symbol_C_temp = {symbol_C_temp}")
  print(f"symbol_C_final= {symbol_C_final}")

  simulator.load()
  simulator.run()

  num_PE = width*height

  # iport maps for A arrays are derived from Leighton's advice
  iportmap_A_val = f"{{ A_val[i=0:{num_PE-1}][j=0:{A_val_len-1}] -> [PE[i % {width}, i // {width}] -> index[j]] }}"
  print(f"iportmap_A_val = {iportmap_A_val}")

  iportmap_A_row_idx = f"{{ A_row_idx[i=0:{num_PE-1}][j=0:{A_rowidx_len-1}] -> [PE[i % {width}, i // {width}] -> index[j]] }}"
  print(f"iportmap_A_row_idx = {iportmap_A_row_idx}")

  iportmap_A_col_ptr = f"{{ A_col_ptr[i=0:{num_PE-1}][j=0:{A_colptr_len-1}] -> [PE[i % {width}, i // {width}] -> index[j]] }}"
  print(f"iportmap_A_col_ptr = {iportmap_A_col_ptr}")

  # B distributes to {py = 0}
  # derived from Residual example code
  iportmap_B = f"{{ B[i=0:{K-1}][j=0:{M-1}] -> [PE[i//{Kt}, 0] ->  index[i%{Kt}, j]] }}"
  print(f"iportmap_B = {iportmap_B}")

  # C_final is gathered from P1.0 and P1.1
  # oport maps for C_final array is dervied from Leighton's advice
  # C_final's size in each PE is Nt*M
  # (Remember: Nt = N // height)
  # Total size: height * Nt * M = N * M 
  oportmap_C_final = f"{{ C_final[n = 0:{N*M-1}] -> [PE[{width-1}, n // {Nt*M}] -> index[n % {Nt*M}]] }}"
  print(f"oportmap_C_final = {oportmap_C_final}")

  # prepare all of A and B via memcpy
  # use the runtime_utils library to calculate memcpy args and shuffle data
  (px, py, w, h, l, data) = runtime_utils.convert_input_tensor(iportmap_A_val, A_val)
  simulator.memcpy_h2d(symbol_A_val, data, False, px, py, w, h, l, 0, False)
  (px, py, w, h, l, data) = runtime_utils.convert_input_tensor(iportmap_A_row_idx, A_row_idx)
  simulator.memcpy_h2d(symbol_A_row_idx, data, False, px, py, w, h, l, 0, False)
  (px, py, w, h, l, data) = runtime_utils.convert_input_tensor(iportmap_A_col_ptr, A_col_ptr)
  simulator.memcpy_h2d(symbol_A_col_ptr, data, False, px, py, w, h, l, 0, False)

  (px, py, w, h, l, data) = runtime_utils.convert_input_tensor(iportmap_B, B)
  simulator.memcpy_h2d(symbol_B, data, False, px, py, w, h, l, 0, False)
  # trigger the computation
  h_params = np.zeros(2).astype(np.uint32)
  # format of h_params
  #  +---------------------+
  #  | # of wvlts          | 1st wavelet
  #  +---------------------+
  #  | param 1             | 2nd wavelet
  #  +---------------------+
  #  | param 2             | 3rd wavelet
  #  +---------------------+
  #  | param 3             | 4th wavelet
  #  +---------------------+
  #  | ...                 |
  #  +---------------------+
  #  | ID of the function  | last wavelet
  #  +---------------------+
  # h_params has K+2 wavelets where K = number of parameters
  h_params[0] = cast_uint32(0) # number of wavelets
  h_params[1] = cast_uint32(np.int16(0)) # ID of the function
  simulator.memcpy_launch(LAUNCH, h_params, False)

  # receive C_final from P1.1 and P1.0
  # use the runtime_utils library to calculate memcpy args and manage output data
  (px, py, w, h, l, data) = runtime_utils.prepare_output_tensor(oportmap_C_final, np.float32)

  # Todo: figure out halt and fire exception in this line
  #simulator.memcpy_d2h(data, symbol_C_final, False, px, py, w, h, l, 0, False)

  C_cs = runtime_utils.format_output_tensor(oportmap_C_final, np.float32, data)

  # todo: Reshape C_cs such that we have it in our original shape


  simulator.stop()

  if args.cmaddr is None:
    # move simulation log and core dump to the given folder
    shutil.move("sim.log", sim_log)

    dst = Path(f"{args.name}/simfab_traces")
    if dst.exists():
      shutil.rmtree(dst)
    shutil.move("simfab_traces", dst)

  print(f"`C_ref`     from CPU:\n{C_ref}")
  print(f"`C_cs`  from CS1 (1-by-1 matrix):\n{C_cs}")

  # todo: Compare results
  
  print("\nSUCCESS!")


if __name__ == "__main__":
  main()