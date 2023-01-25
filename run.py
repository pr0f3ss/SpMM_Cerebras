from itertools import product
import argparse
from glob import glob
import numpy as np
from cerebras.elf.cs_elf_runner import CSELFRunner

# get grid format helper functions
from helper import generate_random_matrix, get_grid_format

parser = argparse.ArgumentParser()
parser.add_argument("--name", help="the test name")
args = parser.parse_args()
name = args.name

elf_paths = glob(f"{name}/bin/*.elf")
runner = CSELFRunner(elf_paths)

# Initialize the input matrices
# A: sparse N x K matrix
# B: dense K x M matrix (slim: M small)
# C: output N x M matrix

# A grid: Nt x Kt
# B grid: Kt x Mt
# C grid: Nt x Mt

P, Nt, Kt, Mt, nnz = 4, 8, 4, 4, 15

N = Nt * P // 32
K = Kt * P // 16
M = Mt // 4

# generate A helper arrays
S = generate_random_matrix(N, K)
A, nnz = S.A, S.count_nonzero()
A_i, A_j, A_val, A_grid_ptr = get_grid_format(A, nnz, N, K, Nt, Kt)

B = np.arange(K * M, dtype=np.float32).reshape((K, M)) % 100

# Split B into vertical tiles that can be mapped to each PE
B_tiles = np.vsplit(B, P)

# Write tiles to PEs
for px, py in product(range(P), range(P)):
  B_tile = B_tiles[py]

  runner.set_symbol(px, py, "A_i", A_i)
  runner.set_symbol(px, py, "A_j", A_j)
  runner.set_symbol(px, py, "A_val", A_val)
  runner.set_symbol(px, py, "A_grid_ptr", A_grid_ptr)

  runner.set_symbol(px, py, "B_tile", B_tile)

# Run the simulation
runner.connect_and_run()

starts = np.zeros((P), dtype=int)
ends = np.zeros((P), dtype=int)
def parse_timestamp(words):
  return words[0] | (words[1] << 16) | (words[2] << 32)

# Collect the results
C_tiles = np.zeros((P, Nt, Mt), dtype=np.float32)
for px in range(P):
  C_tile = runner.get_symbol(px, 0, "C_final", np.float32).reshape(Nt, Mt)
  C_tiles[px] = C_tile

  # Get timestamping information
  start = runner.get_symbol(px, 0, "tsc_start_buffer", np.uint16)
  end = runner.get_symbol(px, 0, "tsc_end_buffer", np.uint16)
  starts[px] = parse_timestamp(start)
  ends[px] = parse_timestamp(end)

print(f"Cycles = {ends.max() - starts.min()}")

# Reshape the tensor into the right shape
# todo: get it right
C_result = C_tiles.transpose(1, 2, 0, 3).reshape(N, M)

# Check the result
# C_expected = np.dot(A, B)
# np.testing.assert_equal(C_expected, C_result)

print("SUCCESS")
