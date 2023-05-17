#!/usr/bin/env bash

set -x
set -e


A_heights=(16 768 768 768 768 4096 4096 4096 4096 4096)
A_widths=(16 4096 4096 4096 4096 4096 4096 4096 4096 4096)
A_densities=(10 10 15 20 30 5 10 15 20 30)
grid_h=(4 64 64 64 64 128 128 128 128 128)
grid_w=(4 64 64 64 64 128 128 128 128 128)
M_w=(8 768 768 768 768 4096 4096 4096 4096 4096)
vector_paths=("CSR_16x16_10")

testlen=${#A_heights[@]}

for (( i=0; i<${testlen}; i++ ));
do
  ./run_benchmark_2.sh ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} ${M_w[i]} ${vector_paths[i]} 
done