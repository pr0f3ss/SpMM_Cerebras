#!/usr/bin/env bash

set -e

A_height=$1
A_width=$2
A_density=$3
grid_height=$4
grid_width=$5
M_width=$6
test_vectors=$7
file_dir="$test_vectors/"

cd $test_vectors

OUTPUT=($(cat out.txt)) # Evaluate output from python script as an array of numbers
# Extract numbers from array indicating padded length of arrays
A_len=${OUTPUT[0]}
echo $A_len
cd ..

cslc ./layout.csl --fabric-dims=757,996 --fabric-offsets=4,1 --params=width:$grid_width,height:$grid_height,Nt:$(($A_height / $grid_height)),Kt:$(($A_width / $grid_width)),M:$M_width,A_len:$A_len,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0

echo "Running simulator now!"

cs_python run_memcpy.py --name out -N=$A_height -K=$A_width -M=$M_width -A_prefix="tmp" -file_dir=$file_dir -width=$grid_width -height=$grid_height -density=$A_density --cmaddr $CS_IP_ADDR:9000

