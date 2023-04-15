
import argparse
from glob import glob
import numpy as np

from cerebras.elf.cs_elf_runner import CSELFRunner
from cerebras.elf.cself import ELFMemory
from cerebras.elf.cs_elf_runner.lib import csl_utils

Pw = 9
Ph = 1
chunk_size = 1

Nx = 10

parser = argparse.ArgumentParser()
parser.add_argument('--name', help='the test name')
parser.add_argument('--cmaddr', help='IP:port for CS system')
args = parser.parse_args()
name = args.name

# Path to ELF files
elf_paths = glob(f"{name}/bin/out_*.elf")

# Simulate ELF files
runner = CSELFRunner(elf_paths, cmaddr=args.cmaddr)

rect = (Pw, Ph)

runner.connect_and_run()

# correct_faddh_result = np.full(Nx, 80, dtype=np.float32)
# rect = ((0, 0), (1, Ph))
faddh_results = runner.get_symbol(0, 0, "data", dtype=np.float32)
print(faddh_results)
# for y in range(Ph):
#   np.testing.assert_equal(faddh_results[0, y], correct_faddh_result)

# correct_gather_recv = np.ones(Ny).astype(np.int32)
# rect = ((0, 0), (Pw, 1))
# gather_recvs = runner.get_symbol_rect(rect, "gather_recv", dtype=np.int32)
# for x in range(Pw):
#   np.testing.assert_equal(gather_recvs[x, 0], correct_gather_recv)
timestamp_output = csl_utils.read_trace(runner, 0, 0, 'times')

# Print out all traces for PE
print("PE (", 0, ", 0): ")
print("Times: ", timestamp_output)
print("SUCCESS")


f = open("results.txt", "a")
f.write(f'{timestamp_output[1] - 48}\n')
f.close()
