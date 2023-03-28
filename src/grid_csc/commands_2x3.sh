#!/usr/bin/env bash

set -e


cslc ./layout.csl --fabric-dims=10,4 --fabric-offsets=4,1 --params=width:3,height:2,Nt:2,Kt:1,M:8,A_val_len:2,A_rowidx_len:2,A_colptr_len:2,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0

echo "Running simulator now!"

cs_python run_memcpy.py --name out -N=4 -K=3 -M=8 -A_prefix="PE2x3_4x3" -width=3 -height=2