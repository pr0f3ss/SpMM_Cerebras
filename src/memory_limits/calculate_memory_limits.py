import numpy as np
import math
import matplotlib.pyplot as plt
import scipy.stats as stats
import xlsxwriter,datetime,os
import itertools
from matplotlib.font_manager import FontProperties
from scipy.stats import norm

from operator import itemgetter

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
    t: number of trials (= PEs = width*height)

    Returns
    -------
    An upper bound (with probabilty 'GUARANTEE') of the elements inside a Nt x Kt submatrix with density 'd' in a total 't' number of trials.
    """

    p = density/100
    n = int(Nt*Kt)

    mean = n * p
    variance = n * p * (1 - p)
    standard_deviation = math.sqrt(variance)

    z = norm.ppf(GUARANTEE**(1/t))
    k = math.ceil(mean + z * standard_deviation)

    return k

def memory_used_coo(Nt, Kt, M, density, width, height):
    """Calculates the memory that is used per PE when using the grid COO format

    Parameters
    ----------
    Nt: dimension Nt = N / grid_height
    Kt: dimension Kt = K / grid_width
    M: dimension M 
    density: density of the matrix A

    Returns
    -------
    Memory in bytes being used per PE
    """
    # Calculate alignment and padding of M in implementation
    align = 16
    multiple = int(align/4)
    padded_M = math.ceil((M+1)/multiple)*multiple

    # Calculate upper bound of nnz inside submatrix (0 <= upper_nnz <= Nt*Kt)
    upper_nnz = find_upper_bound_nnz(Nt, Kt, density, width*height)

    # Calculate the number of 4 byte elements
    # Rest of buffers accounted for in reserved memory
    mem_B = Kt*padded_M
    mem_C = Nt*padded_M
    mem_A_val = upper_nnz
    mem_A_x = upper_nnz
    mem_A_y = upper_nnz

    return 4*(mem_B+mem_C+mem_A_val+mem_A_x+mem_A_y)

def memory_used_csr(Nt, Kt, M, density, width, height):
    """Calculates the memory that is used per PE when using the grid CSR format

    Parameters
    ----------
    Nt: dimension Nt = N / grid_height
    Kt: dimension Kt = K / grid_width
    M: dimension M 
    density: density of the matrix A

    Returns
    -------
    Memory in bytes being used per PE
    """
    # Calculate alignment and padding of M in implementation
    align = 16
    multiple = int(align/4)
    padded_M = math.ceil((M+1)/multiple)*multiple

    # Calculate upper bound of nnz inside submatrix (0 <= upper_nnz <= Nt*Kt)
    upper_nnz = find_upper_bound_nnz(Nt, Kt, density, width*height)

    # Calculate the number of 4 byte elements
    # Rest of buffers accounted for in reserved memory
    mem_B = Kt*padded_M
    mem_C = Nt*padded_M
    mem_A_val = upper_nnz
    mem_A_rowptr = Nt+1
    mem_A_colidx = upper_nnz

    return 4*(mem_B+mem_C+mem_A_val+mem_A_rowptr+mem_A_colidx)

def memory_used_csc(Nt, Kt, M, density, width, height):
    """Calculates the memory that is used per PE when using the grid CSC format

    Parameters
    ----------
    Nt: dimension Nt = N / grid_height
    Kt: dimension Kt = K / grid_width
    M: dimension M 
    density: density of the matrix A

    Returns
    -------
    Memory in bytes being used per PE
    """
    # Calculate alignment and padding of M in implementation
    align = 16
    multiple = int(align/4)
    padded_M = math.ceil((M+1)/multiple)*multiple

    # Calculate upper bound of nnz inside submatrix (0 <= upper_nnz <= Nt*Kt)
    upper_nnz = find_upper_bound_nnz(Nt, Kt, density, width*height)

    # Calculate the number of 4 byte elements
    # Rest of buffers accounted for in reserved memory
    mem_B = Kt*padded_M
    mem_C = Nt*padded_M
    mem_A_val = upper_nnz
    mem_A_rowidx = upper_nnz
    mem_A_colptr = Kt+1

    return 4*(mem_B+mem_C+mem_A_val+mem_A_rowidx+mem_A_colptr)

def memory_used_ellpack(Nt, Kt, M, density, width, height):
    """Calculates the memory that is used per PE when using the grid ellpack format

    Parameters
    ----------
    Nt: dimension Nt = N / grid_height
    Kt: dimension Kt = K / grid_width
    M: dimension M 
    density: density of the matrix A

    Returns
    -------
    Memory in bytes being used per PE
    """
    # Calculate alignment and padding of M in implementation
    align = 16
    multiple = int(align/4)
    padded_M = math.ceil((M+1)/multiple)*multiple

    # Calculate upper bound of nnz inside submatrix (0 <= upper_nnz <= Nt*Kt)
    upper_nnz = find_upper_bound_nnz(Nt, Kt, density, width*height)

    # Calculate the number of 4 byte elements
    # Rest of buffers accounted for in reserved memory
    mem_B = Kt*padded_M
    mem_C = Nt*padded_M
    mem_A_val = upper_nnz
    mem_A_indices = upper_nnz

    return 4*(mem_B+mem_C+mem_A_val+mem_A_indices)

def memory_used_gemm(Nt, Kt, M, density, width, height):
    """Calculates the memory that is used per PE when using GEMM

    Parameters
    ----------
    Nt: dimension Nt = N / grid_height
    Kt: dimension Kt = K / grid_width
    M: dimension M 
    density: density of the matrix A

    Returns
    -------
    Memory in bytes being used per PE
    """
    # Calculate alignment and padding of M in implementation
    align = 16
    multiple = int(align/4)
    padded_M = math.ceil((M+1)/multiple)*multiple

    # Calculate the number of 4 byte elements
    # Rest of buffers accounted for in reserved memory
    mem_B = Kt*padded_M
    mem_C = Nt*padded_M
    mem_A = Nt*Kt

    return 4*(mem_B+mem_C+mem_A)

density_list = [5, 10, 20, 30]
NK_list = [(768, 768) , (3072, 768), (768, 3072), (1024,1024), (4096, 1024), (1024, 4096)]

f_out = []

for density in density_list:
    for (N,K) in NK_list:
        output = []
        for M in [32, 64, 128, 256, 512]:
            grid_height_list = [i for i in range(1, AVAIL_HEIGHT) if N % i == 0]
            grid_width_list = [i for i in range(1, AVAIL_WIDTH) if K % i == 0]

            zipped = list(itertools.product(grid_height_list,grid_width_list))

            # Change which format is used here:
            mem_used = [memory_used_gemm(int(N/h), int(K/w), M, density, w, h) for (h,w) in zipped]

            grid_height_list = [x[0] for x in zipped]
            grid_width_list = [x[1] for x in zipped]

            # Get configs that fit in a PE
            configs = [(mem_used[i], grid_height_list[i], grid_width_list[i], (N/grid_height_list[i])*(K/grid_width_list[i]), int(M)) for i in range(len(grid_width_list)) if mem_used[i] < MEM-RESERVED]
            best_config = sorted(configs, key=itemgetter(0))[-1]
            mem_max = best_config[0]

            # Get all configs that are within 5% range
            for config in configs:
                mem = config[0]
                if mem_max - (mem_max*0.05) < mem:
                    output.append((mem, config[1], config[2], config[3], config[4]))


        # Sort by Nt x Kt first (4th element) and extract highest amount
        max_ntkt = sorted(output, key=itemgetter(3))[-1][3]
        # Extract all configs with highest Nt x Kt
        ntkt_config = [c for c in output if max_ntkt==c[3]]
        # Sort by memory used and choose largest
        best_config = sorted(ntkt_config, key=itemgetter(0))[-1]
        mem_max = best_config[0]

        result = []
        # Get all configs that are within 5% range
        for config in ntkt_config:
            mem = config[0]
            if mem_max - (mem_max*0.05) < mem:
                result.append((mem, config[1], config[2], config[3], config[4]))

        # Sort by M and extract highest M
        max_M = sorted(result, key=itemgetter(4))[-1][4]
        final_output = [c for c in result if max_M==c[4]]

        # If there are multiple ones, just use first option
        _, w, h, _, m = final_output[0]
        f_out.append([N, K, density, h, w, m])

# Print final output
print(f"A_heights=({' '.join([str(x[0]) for x in f_out])})")
print(f"A_widths=({' '.join([str(x[1]) for x in f_out])})")
print(f"A_densities=({' '.join([str(x[2]) for x in f_out])})")
print(f"grid_h=({' '.join([str(x[3]) for x in f_out])})")
print(f"grid_w=({' '.join([str(x[4]) for x in f_out])})")
print(f"M_w=({' '.join([str(x[5]) for x in f_out])})")
        





