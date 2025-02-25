#!/usr/bin/env bash

set -e

A_height=$1
A_width=$2
A_density=$3
grid_height=$4
grid_width=$5
M_width=$6

cslc ./layout.csl --fabric-dims=$(($grid_width + 7)),$(($grid_height + 2)) --fabric-offsets=4,1 --params=width:$grid_width,height:$grid_height,Nt:$(($A_height / $grid_height)),Kt:$(($A_width / $grid_width)),M:$M_width,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0

echo "Running simulator now!"

cs_python run_memcpy.py --name out -N=$A_height -K=$A_width -M=$M_width -width=$grid_width -height=$grid_height -density=$A_density

