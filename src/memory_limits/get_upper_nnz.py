import scipy.stats as stats
import math
from scipy.stats import norm

# Defines the memory available per PE
MEM = 48*1024
RESERVED = 6*1024 # Reserve 6 kB of memory for program, dsd buffers etc.
GUARANTEE = 0.99
AVAIL_HEIGHT = 996
AVAIL_WIDTH = 757

def find_upper_bound_nnz(Nt, Kt, density, t):
    """Calculates an upper bound of elements 'x' in a Nt x Kt submatrix generated with density 'd'
    in a total t number of trials.
    The upper bound is guaranteed with probabilty at least 'GUARANTEE'

    Parameters
    ----------
    Nt: dimension Nt = N / grid_height
    Kt: dimension Kt = K / grid_width
    density: density of the matrix A
    t: number of trials (= PEs)

    Returns
    -------
    An upper bound (with probabilty 'GUARANTEE') of the elements inside a Nt x Kt submatrix with density 'd'.
    """

    p = density/100
    n = int(Nt*Kt)

    mean = n * p
    variance = n * p * (1 - p)
    standard_deviation = math.sqrt(variance)

    z = norm.ppf(GUARANTEE**(1/t))
    k = math.ceil(mean + z * standard_deviation)

    return k

Nt = 768/16
Kt = 768/6
density = 20
t = 16*6

print(find_upper_bound_nnz(Nt, Kt, density, t))
