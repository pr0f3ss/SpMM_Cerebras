#!/usr/bin/env bash

set -x
set -e

A_heights=(768 3072 768 1024 4096 1024)
A_widths=(768 768 3072 1024 1024 4096)
A_densities=(20 20 20 20 20 20)
grid_h=(16 24 16 8 32 128)
grid_w=(6 16 24 128 128 32)
M_w=(32 32 32 64 64 64)

testlen=${#A_heights[@]}

for (( i=0; i<${testlen}; i++ ));
do
  vector_path="COO_${A_heights[i]}x${A_widths[i]}_${A_densities[i]}"
  ./run_benchmark.sh ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} ${M_w[i]} $vector_path
done