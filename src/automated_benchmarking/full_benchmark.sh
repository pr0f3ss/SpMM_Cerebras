#!/usr/bin/env bash

set -x
set -e

A_heights=(32 32 32 32 32 32 32 32 32 32 32 32)
A_widths=(32 32 32 32 32 32 32 32 32 32 32 32)
A_densities=(5 10 20 100 5 10 20 100 5 10 20 100)
grid_h=(4 4 4 4 8 8 8 8 16 16 16 16)
grid_w=(4 4 4 4 8 8 8 8 16 16 16 16)
M_w=(16 16 16 16 16 16 16 16 16 16 16 16)

testlen=${#A_heights[@]}

for (( i=0; i<${testlen}; i++ ));
do
  ./run_benchmark.sh ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} ${M_w[i]} 
done

mv ../grid_csc/benchmark_results.txt results/csc_benchmark_results.txt
mv ../grid_csr/benchmark_results.txt results/csr_benchmark_results.txt
mv ../grid_custom/benchmark_results.txt results/custom_benchmark_results.txt