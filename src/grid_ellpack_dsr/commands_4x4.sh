#!/usr/bin/env bash

set -e

# IMPORTANT: Have to extend A_len by 1 for it to work!!!
cslc ./layout.csl --fabric-dims=12,6 --fabric-offsets=4,1 --params=width:2,height:2,Nt:4,Kt:4,M:8,A_len:4,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0

echo "Running simulator now!"

cs_python run_memcpy.py --name out -N=8 -K=8 -M=8 -A_prefix="tmp" -width=2 -height=2