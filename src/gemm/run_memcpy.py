#!/usr/bin/env cs_python
# pylint: disable=line-too-long

""" Compute A*B using a height-by-width PE rectangle

   The height-by-width rectangle is surrounded by a halo of size 1.
   The halo is used to route the input and output data between the host and the device.
   It does not impact the layout index of the kernel code.
   For example, the kernel has 2-by-2 PEs, with the index P0.0, P1.0, P0.1, P1.1
   in the layout/routing configuration.
   The compiler generates ELFs out_0_0.elf, out_0_1.elf, out_1_0.elf and out_1_1.elf.
   However the user needs global coordinate (including halo) for debugging, for example
   P0.0 of the kernel is P1.1 when the user calls sdk_debug_shell to dump the trace or
   landing log.

   The workflow goes as follows:
   Memcpy of A (and B in the first row)
   Each PE receives B from north and broadcasts B to the south
   Each PE computes its local A*B
   Each PE reduces its local C to the east
   Last column has the result A*B = C from its rows.

   To simplify the example, the dimensions N and K are divisible by height and width respectively.

   The matrix B is distributed into columns. The first row receives B from the fabric,
   then broadcasts B into other rows.

   One can use the following command to check the landing log of P0.0:
    sdk_debug_shell wavelet-trace --artifact_dir . --x 1 --y 1 trace

"""


import os
import struct
import argparse
from pathlib import Path
from typing import Optional
import shutil
import subprocess
import numpy as np
import math
import csv

from cerebras.sdk.runtime import runtime_utils # pylint: disable=no-name-in-module
from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime # pylint: disable=no-name-in-module
from cerebras.sdk.runtime.sdkruntimepybind import MemcpyDataType # pylint: disable=no-name-in-module
from cerebras.sdk.runtime.sdkruntimepybind import MemcpyOrder    # pylint: disable=no-name-in-module

FILE_PATH = os.path.realpath(__file__)
RESIDUAL_DIR = os.path.dirname(FILE_PATH)
BENCHMARKS_DIR = os.path.dirname(RESIDUAL_DIR)
CSL_DIR = os.path.dirname(BENCHMARKS_DIR)
CSLC = os.path.join(CSL_DIR, "build") + "/bin/cslc"

def split_matrix_into_grids(matrix, Nt, Kt):
    N, K = matrix.shape
    submatrices = []
    for i in range(0, N, Nt):
        for j in range(0, K, Kt):
            submatrix = matrix[i:i+Nt, j:j+Kt].flatten()
            submatrices.append(submatrix)
    return np.array(submatrices)


def float_to_hex(f):
  return hex(struct.unpack('<I', struct.pack('<f', f))[0])

def make_u48(words):
  return words[0] + (words[1] << 16) + (words[2] << 32)

def sub_ts(words):
      return make_u48(words[3:]) - make_u48(words[0:3])

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
                      help="number of rows of the A and C/C_final")
  parser.add_argument("-K", type=int,
                      help="number of columns of the  A and number of rows of B")
  parser.add_argument("-M", type=int,
                      help="number of columns of the matrix B and C.")
  parser.add_argument("-A_prefix", type=str,
                      help="prefix of the dense matrix file")
  parser.add_argument("-file_dir", type=str,
                      help="directory for vectors")
  parser.add_argument("-width", type=int,
                      help="width of PEs")
  parser.add_argument("-height", type=int,
                      help="height of PEs")
  parser.add_argument("-density", type=int,
                      help="density of A in percent")
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
    args.append(f"--params=Nt:{Nt}, Kt:{Kt}, M:{M}") # options

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

# Set up params and fill in missing params
  if args.width is not None:
    width = args.width
  else:
    width = 2

  if args.height is not None:
    height = args.height
  else:
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

  if args.file_dir is not None:
    file_dir = args.file_dir
  else:
    file_dir = "test_vectors/"

  if args.density is not None:
    density = args.density
  else:
    density = 100

  Nt = N // height
  Kt= K // width

  assert N == (Nt*height), "N must be multiple of Nt"
  assert K == (Kt*width), "K must be multiple of Kt"

  Nt = int(Nt)
  Kt = int(Kt)

  print(f"N = {N}, K = {K}, M = {M}, width = {width}, height = {height}")

  # Use this for reference solution
  A_dense_format = file_dir+A_prefix+".csv"
  A = np.genfromtxt(A_dense_format, delimiter=",", dtype=np.float32).reshape(N, K)

  np.random.seed(2)
  
  B = np.arange(K*M).reshape(K, M).astype(np.float32) + 100

  C_ref = np.matmul(A, B)
  print(f"C_ref = {C_ref}")
  print(f"A = {A}")
  print(f"B = {B}")
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
      M,
      Nt,
      Kt,
      n_channels,
      width_west_buf,
      width_east_buf)
  if args.compile:
    print("COMPILE ONLY: EXIT")
    return

  memcpy_dtype = MemcpyDataType.MEMCPY_32BIT
  memcpy_order = MemcpyOrder.ROW_MAJOR

  simulator = SdkRuntime(args.name, cmaddr=args.cmaddr)

  symbol_A = simulator.get_id("A")
  symbol_B = simulator.get_id("B")
  symbol_C = simulator.get_id("C")
  symbol_time_memcpy = simulator.get_id("time_memcpy")

  print(f"symbol_A = {symbol_A}")
  print(f"symbol_x = {symbol_B}")
  print(f"symbol_C= {symbol_C}")

  simulator.load()
  simulator.run()

  num_PE = width*height

  A_prep = split_matrix_into_grids(A, Nt, Kt).reshape(height,width, Nt*Kt)

  # derived from Residual example code
  iportmap_A = f"{{ A_prep[i=0:{height-1}][j=0:{width-1}][k=0:{Nt*Kt-1}] -> [PE[j, i] ->  index[k]] }}"
  print(f"iportmap_A = {iportmap_A}")

  # B distributes to {py = 0}
  # derived from Residual example code
  iportmap_B = f"{{ B[i=0:{K-1}][j=0:{M-1}] -> [PE[i//{Kt}, 0] ->  index[i%{Kt}, j]] }}"
  print(f"iportmap_B = {iportmap_B}")

  # C is gathered from P1.0 and P1.1
  # oport maps for C array is dervied from Leighton's advice
  # C's size in each PE is Nt*M
  # (Remember: Nt = N // height)
  # Total size: height * Nt * M = N * M 
  oportmap_C = f"{{ C[n = 0:{N*M-1}] -> [PE[{width-1}, n // {Nt*M}] -> index[n % {Nt*M}]] }}"
  print(f"oportmap_C = {oportmap_C}")

  # prepare all of A and B via memcpy
  # use the runtime_utils library to calculate memcpy args and shuffle data

  (px, py, w, h, l, data) = runtime_utils.convert_input_tensor(iportmap_B, B)
  simulator.memcpy_h2d(symbol_B, data, px, py, w, h, l,
                     streaming=False, data_type=memcpy_dtype, nonblock=False,
                     order=memcpy_order)

  (px, py, w, h, l, data) = runtime_utils.convert_input_tensor(iportmap_A, A_prep)
  simulator.memcpy_h2d(symbol_A, data, px, py, w, h, l,
                     streaming=False, data_type=memcpy_dtype, nonblock=False,
                     order=memcpy_order)

  simulator.call("bcast_B", [], nonblock=False)

  # receive C from P1.1 and P1.0
  # use the runtime_utils library to calculate memcpy args and manage output data
  (px, py, w, h, l, data) = runtime_utils.prepare_output_tensor(oportmap_C, np.float32)
  simulator.memcpy_d2h(data, symbol_C, px, py, w, h, l,
                     streaming=False, data_type=memcpy_dtype, nonblock=False,
                     order=memcpy_order)

  C_cs = runtime_utils.format_output_tensor(oportmap_C, np.float32, data)

  # Reshape back to original state
  C_cs = np.reshape(C_cs, (N, M))

  # Copy back timestamps
  data = np.zeros((width*height*3, 1), dtype=np.float32)
  simulator.memcpy_d2h(data, symbol_time_memcpy, 0, 0, width, height, 3,
    streaming=False, data_type=MemcpyDataType.MEMCPY_32BIT, order=MemcpyOrder.ROW_MAJOR, nonblock=False)
  maxmin_time_hwl = data.view(np.float32).reshape((height, width, 3))

  simulator.stop()

  tsc_tensor_d2h = np.zeros(6).astype(np.uint16)
  min_cycles = math.inf
  max_cycles = 0
  avg_cycles = 0
  for w in range(width):
    for h in range(height):
      hex_t0 = int(float_to_hex(maxmin_time_hwl[(h, w, 0)]), base=16)
      hex_t1 = int(float_to_hex(maxmin_time_hwl[(h, w, 1)]), base=16)
      hex_t2 = int(float_to_hex(maxmin_time_hwl[(h, w, 2)]), base=16)
      tsc_tensor_d2h[0] = hex_t0 & 0x0000ffff
      tsc_tensor_d2h[1] = (hex_t0 >> 16) & 0x0000ffff
      tsc_tensor_d2h[2] = hex_t1 & 0x0000ffff
      tsc_tensor_d2h[3] = (hex_t1 >> 16) & 0x0000ffff
      tsc_tensor_d2h[4] = hex_t2 & 0x0000ffff
      tsc_tensor_d2h[5] = (hex_t2 >> 16) & 0x0000ffff

      cycles = sub_ts(tsc_tensor_d2h)
      avg_cycles += cycles
      if cycles < min_cycles:
        min_cycles = cycles
        min_w = w
        min_h = h
      if cycles > max_cycles:
        max_cycles = cycles
        max_w = w
        max_h = h

  avg_cycles //= height*width

  #####################
  # Calculate bandwidth
  #####################

  # Iterate over Kt: Read A column -> Iterate over M: Read C column and read one element
  # = 4*Kt*(Nt+M*(Nt+1))
  # For absolute accesses also include writes to C and additional A read inside M loop = 4*Kt*(Nt+M*(3*Nt+1))

  total_relative_accesses = width * height * (4*Kt*(Nt+M*(Nt+1)))
  total_absolute_accesses = width * height * (4*Kt*(Nt+M*(3*Nt+1)))
  total_flop = width * height * (Kt*M*2*Nt)

  #################
  # Generate output
  #################

  print()
  print("Cycle Counts:")
  print("Min cycles (", min_w, ", ", min_h, "): ", min_cycles)
  print("Max cycles (", max_w, ", ", max_h, "): ", max_cycles)
  print()
  print("Accesses and FLOP Information:")
  print("Relative accesses (bytes): ", total_relative_accesses)
  print("Absolute accesses (bytes): ", total_absolute_accesses)
  print("FP operations:             ", total_flop)
  print()

  # Write a CSV
  csv_name = f"GEMM_benchmark" + ".csv"
  with open(csv_name, mode='a') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([width, height, N, K, M, density, avg_cycles, min_cycles, max_cycles,
      total_relative_accesses, total_absolute_accesses,  total_flop])

  if args.cmaddr is None:
    #move simulation log and core dump to the given folder
    shutil.move("sim.log", sim_log)

    dst = Path(f"{args.name}/simfab_traces")
    if dst.exists():
      shutil.rmtree(dst)
    shutil.move("simfab_traces", dst)

  print(f"`C_ref`     from CPU:\n{C_ref}")
  print(f"`C_cs`  from CS1 (1-by-1 matrix):\n{C_cs}")

  assert np.allclose(C_ref, C_cs, 1.e-5)

  
  print("\nSUCCESS!")


if __name__ == "__main__":
  main()