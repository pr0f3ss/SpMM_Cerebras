#!/usr/bin/env bash

set -e

A_height=$1
A_width=$2
A_density=$3
grid_height=$4
grid_width=$5
M_width=$6
i=3

cd test_vectors
# Generate A matrix
./a.out $A_height $A_width $A_density $grid_height $grid_width $i
OUTPUT=($(python3 add_padding.py 3 | tr -d '[],')) # Evaluate output from python script as an array of numbers
# Extract numbers from array indicating padded length of arrays
A_len=${OUTPUT[1]}
idx_len=${OUTPUT[3]}

cd ..

# IMPORTANT: Have to extend A_len by 1 for it to work!!!
cslc ./layout.csl --fabric-dims=$(($grid_width + 7)),$(($grid_height + 2)) --fabric-offsets=4,1 --params=width:$grid_width,height:$grid_height,Nt:$(($A_height / $grid_height)),Kt:$(($A_width / $grid_width)),M:$M_width,A_len:$(($A_len + 1)) ,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0

echo "Running simulator now!"

cs_python run_memcpy.py --name out -N=$A_height -K=$A_width -M=$M_width -A_prefix="test" -width=$grid_width -height=$grid_height

