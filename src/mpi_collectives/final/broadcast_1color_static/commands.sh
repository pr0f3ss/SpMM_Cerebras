#!/usr/bin/env bash

set -e

cslc ./layout.csl --fabric-dims=128,1 \
--fabric-offsets=0,0 -o out
cs_python run.py --name out