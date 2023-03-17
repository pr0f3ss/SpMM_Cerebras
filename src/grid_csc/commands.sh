#!/usr/bin/env bash

set -e

# Question: is N height and K width of A or is it opposite? 
A_height=8
A_width=8
A_density=20
grid_height=2
grid_width=2

# Generate A matrix
cd test_vectors
./a.out 8 8 20 2 2
OUTPUT=($(python3 add_padding.py | tr -d '[],'))

val_len=${OUTPUT[0]} 
row_idx_len=${OUTPUT[1]}
col_ptr_len=${OUTPUT[2]}
cd ..

cslc ./layout.csl --fabric-dims=9,4 --fabric-offsets=4,1 --params=width:$grid_width,height:$grid_height,Nt:$(($A_height / $grid_height)),Kt:$(($A_width / $grid_width)),M:8,A_val_len:$val_len,A_rowidx_len:$row_idx_len,A_colptr_len:$col_ptr_len,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0

echo "Running simulator now!"

cs_python run_memcpy.py --name out -N=$A_height -K=$A_width -M=8 -A_prefix="test"