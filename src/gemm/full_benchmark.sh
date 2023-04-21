#!/usr/bin/env bash

set -x
set -e

A_heights=(80)
A_widths=(80)
A_densities=(5)
grid_h=(4)
grid_w=(4)
M_w=(16)

testlen=${#A_heights[@]}

for (( i=0; i<${testlen}; i++ ));
do
  ./run_benchmark.sh ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} ${M_w[i]} 
done