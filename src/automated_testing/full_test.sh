#!/usr/bin/env bash

set -x
set -e

A_heights=(6 10 18)
A_widths=(6 10 12)
A_densities=(50 25 10)
grid_h=(2 5 6)
grid_w=(2 5 3)
M_w=(8 10 12)

testlen=${#A_heights[@]}

for (( i=1; i<${testlen}; i++ ));
do
  ./run_test.sh ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} ${M_w[i]} 
done


