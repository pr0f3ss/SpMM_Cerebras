#!/usr/bin/env bash

set -e


cslc ./layout.csl --fabric-dims=11,6 --fabric-offsets=4,1 --params=width:4,height:4,Nt:3,Kt:3,M:8,A_val_len:9,A_colidx_len:9,A_rowptr_len:4,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0

echo "Running simulator now!"

cs_python run_memcpy.py --name out -N=12 -K=12 -M=8 -A_prefix="PE4x4_12x12" -width=4 -height=4