#!/usr/bin/env bash

set -x
set -e

A_heights=(16)
A_widths=(16)
A_densities=(15)
grid_h=(2)
grid_w=(4)
M_w=(32)

testlen=${#A_heights[@]}

for (( i=0; i<${testlen}; i++ ));
do
  ./run_test.sh ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} ${M_w[i]} 
done


