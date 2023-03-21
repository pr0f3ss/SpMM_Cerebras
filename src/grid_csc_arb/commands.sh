#!/usr/bin/env bash

set -e


cslc ./layout.csl --fabric-dims=9,4 --fabric-offsets=4,1 --params=width:2,height:2,Nt:3,Kt:3,M:8,A_val_len:3,A_rowidx_len:3,A_colptr_len:4,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0

echo "Running simulator now!"

cs_python run_memcpy.py --name out -N=6 -K=6 -M=8 -A_prefix="PE2x2_6x6" -width=2 -height=2