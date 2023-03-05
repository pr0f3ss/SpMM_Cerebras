#!/usr/bin/env bash

set -e

cslc ./layout.csl --fabric-dims=8,8 \
--fabric-offsets=0,0 -o out
cs_python run.py --name out