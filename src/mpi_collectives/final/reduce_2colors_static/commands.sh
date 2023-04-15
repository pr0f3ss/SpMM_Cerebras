#!/usr/bin/env bash

set -e

# for i in {0..15}
# do
#   cslc ./layout.csl --fabric-dims=512,1 \
#   --fabric-offsets=0,0 --params=Nx:$((2**i)) -o out
#   cs_python run.py --name out
# done

cslc ./layout.csl --fabric-dims=4,1 \
  --fabric-offsets=0,0 --params=Nx:16 -o out
  cs_python run.py --name out


