#!/usr/bin/env bash

set -e

cslc ./layout.csl --fabric-dims=14,8 --fabric-offsets=4,1 --params=width:4,height:4,Nt:8,Kt:8,M:16,A_len:8,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0

echo "Running simulator now!"

cs_python run_memcpy.py --name out -N=32 -K=32 -M=16 -A_prefix="tmp" -width=4 -height=4