#!/usr/bin/env bash

set -e


cslc ./layout.csl --fabric-dims=10,5 --fabric-offsets=4,1 --params=width:3,height:3,Nt:2,Kt:2,M:8,A_val_len:2,A_rowidx_len:2,A_colptr_len:3,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0

echo "Running simulator now!"

cs_python run_memcpy.py --name out -N=6 -K=6 -M=8 -A_prefix="PE3x3" -width=3 -height=3