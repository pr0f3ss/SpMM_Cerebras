#!/usr/bin/env bash

set -x
set -e

A_heights=(2)
A_widths=(2)
A_densities=(100)
grid_h=(2)
grid_w=(2)
M_w=(5120)

for (( i=0; i<1; i++ ));
do
  vector_path="COO_${A_heights[i]}x${A_widths[i]}_${A_densities[i]}"
  ./run_benchmark.sh ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} ${M_w[i]} $vector_path
done