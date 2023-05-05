#!/usr/bin/env python3
from pprint import pprint

import matplotlib.pyplot as plt

CLOCK_SPEED=1100000000
FLOPS_PER_CYCLE=4
BANDWIDTH=23500000000
BYTES_PER_CYCLE=BANDWIDTH/CLOCK_SPEED
arith_intensity=10


def frange(start, stop, step=1.0):
    f = start
    while f < stop:
        f += step
        yield f

# Plot configuration
height = 0.8

fig = plt.figure(frameon=False)
ax = fig.add_subplot(1, 1, 1)

yticks_labels = []
yticks = []
xticks_labels = []
xticks = [i for i in range(-4, 4)]

ax.set_xlabel('arithmetic intensity [FLOP/byte]')
ax.set_ylabel('performance [FLOP/cycle]')

# Upper bound
x = list(frange(min(xticks), max(xticks), 0.01))

ax.plot(x, [min(BYTES_PER_CYCLE, FLOPS_PER_CYCLE) for x in x])

# Code location
ax.plot(1, 1, 'r+', markersize=12, markeredgewidth=4)

ax.tick_params(axis='y', which='both', left='off', right='off')
ax.tick_params(axis='x', which='both', top='off')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim(min(xticks), max(xticks))
ax.set_yticks([FLOPS_PER_CYCLE, FLOPS_PER_CYCLE])
ax.set_xticks(xticks+[arith_intensity])
ax.grid(axis='x', alpha=0.7, linestyle='--')
fig.savefig('out.pdf')
plt.show()