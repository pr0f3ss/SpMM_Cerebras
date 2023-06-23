#!/usr/bin/env bash

set -x
set -e

A_heights=(16 32 30 28)
A_widths=(16 32 30 15)
A_densities=(20 30 5 10)
grid_h=(4 2 5 7)
grid_w=(4 4 5 3)
M_w=(32 31 30 29)

# Remove test directories
rm -rf ../gemm/test_vectors
rm -rf ../grid_csc/test_vectors
rm -rf ../grid_csr/test_vectors
rm -rf ../grid_coo/test_vectors
rm -rf ../grid_ellpack/test_vectors

testlen=${#A_heights[@]}

for (( i=0; i<${testlen}; i++ ));
do
  ./run_test.sh ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} ${M_w[i]} 
done


