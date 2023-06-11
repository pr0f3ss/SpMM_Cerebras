#!/usr/bin/env bash

set -x
set -e


source ../memory_limits/CSC_params.txt

testlen=${#A_heights[@]}

for (( i=0; i<${testlen}; i++ ));
do
  vector_path="CSC_${A_heights[i]}x${A_widths[i]}_${A_densities[i]}"
  ./run_benchmark.sh ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} ${M_w[i]} $vector_path
done