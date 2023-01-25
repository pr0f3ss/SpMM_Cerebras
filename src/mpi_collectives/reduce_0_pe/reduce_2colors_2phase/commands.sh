#!/usr/bin/env bash

set -e

# for i in {1..9}
# do
#   cslc ./layout.csl --fabric-dims=512,1 \
#   --fabric-offsets=0,0 --params=Nx:4096,step:$((2**i)) -o out
#   cs_python run.py --name out
# done


cslc ./layout.csl --fabric-dims=512,1 \
  --fabric-offsets=0,0 --params=Nx:64,step:28 -o out
  cs_python run.py --name out