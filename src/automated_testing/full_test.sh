#!/usr/bin/env bash

set -x
set -e

A_heights=(16)
A_widths=(16)
A_densities=(100)
grid_h=(2)
grid_w=(2)
M_w=(32)

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


