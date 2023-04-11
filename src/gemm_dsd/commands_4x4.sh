#!/usr/bin/env bash

set -e

A_height=32
A_width=32
A_density=100
grid_height=16
grid_width=16
M_width=16

cd test_vectors
# Generate A matrix
./a.out $A_height $A_width $A_density $grid_height $grid_width
OUTPUT=($(python3 add_padding.py | tr -d '[],')) # Evaluate output from python script as an array of numbers
# Extract numbers from array indicating padded length of arrays
val_len=${OUTPUT[0]} 
row_idx_len=${OUTPUT[1]}
col_ptr_len=${OUTPUT[2]}
cd ..

# Run compilation
cslc ./layout.csl --fabric-dims=24,19 --fabric-offsets=4,1 --params=width:$grid_width,height:$grid_height,Nt:$(($A_height / $grid_height)),Kt:$(($A_width / $grid_width)),M:$M_width,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0

echo "Running simulator now!"

# Test with sim
cs_python run_memcpy.py --name out -N=$A_height -K=$A_width -M=$M_width -A_prefix="test" -width=$grid_width -height=$grid_height
