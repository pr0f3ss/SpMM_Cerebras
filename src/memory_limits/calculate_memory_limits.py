# This file calculates the memory limits for each of the sparse grid formats

import numpy as np
import math
import matplotlib.pyplot as plt
import scipy.stats as stats
import datetime,os
import itertools
from matplotlib.font_manager import FontProperties
from scipy.stats import norm
import subprocess
from tqdm import tqdm

from operator import itemgetter

# Defines the memory available per PE
MEM = 48*1024
RESERVED = 6*1024 # Reserve 6 kB of memory for program, dsd buffers etc.
GUARANTEE = 0.99
AVAIL_HEIGHT = 996
AVAIL_WIDTH = 757

def get_nnz_csc(N, K, height, width, density):
    """Gets A_val_len, A_colidx_len, A_rowptr_len from a CSC formatted matrix.

    Parameters
    ----------
    N: row dimension
    K: column dimension
    height: grid height
    width: grid width
    density: density of the matrix A

    Returns
    -------
    A_len, A_colidx_len, A_rowptr_len for the submatrices defined by N x K and height x width PEs.
    """

    # Generate the matrix format
    retrieve_params = subprocess.check_output(f"./a.out {N} {K} {density} {height} {width} 0", shell=True, universal_newlines=True)

    # Process the output of the second file
    lines = retrieve_params.splitlines()

    return int(lines[0]), int(lines[1]), int(lines[2])

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

    # Get B and C sizes
    mem_B = Kt*padded_M
    mem_C = Nt*padded_M

    # We first estimate the memory so we can skip unnecessary computations
    upper_nnz = Nt*Kt*(density/100) # calculate the mean nnz
    upper_nnz -= upper_nnz*0.2 # Give some buffer
    mem_A_val = upper_nnz
    mem_A_rowidx = upper_nnz
    mem_A_colptr = Kt+1

    mem_estimate = 4*(mem_B+mem_C+mem_A_val+mem_A_colptr+mem_A_rowidx)
    if(mem_estimate > MEM-RESERVED):
        return mem_estimate

    # If estimated memory is within range, we do the actual computation
    A_val_len, A_rowidx_len, A_colptr_len = get_nnz_csc(int(Nt*height), int(Kt*width), height, width, density)

    # Use actual sizes
    mem_A_val = A_val_len
    mem_A_rowidx = A_rowidx_len
    mem_A_colptr = A_colptr_len

    return 4*(mem_B+mem_C+mem_A_val+mem_A_colptr+mem_A_rowidx)

def get_nnz_csr(N, K, height, width, density):
    """Gets A_val_len, A_rowidx_len, A_colptr_len from a CSR formatted matrix.

    Parameters
    ----------
    N: row dimension
    K: column dimension
    height: grid height
    width: grid width
    density: density of the matrix A

    Returns
    -------
    A_len, A_rowidx_len, A_colptr_len for the submatrices defined by N x K and height x width PEs.
    """

    # Generate the matrix format
    retrieve_params = subprocess.check_output(f"./a.out {N} {K} {density} {height} {width} 1", shell=True, universal_newlines=True)

    # Process the output of the second file
    lines = retrieve_params.splitlines()

    return int(lines[0]), int(lines[1]), int(lines[2])

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

    # Get B and C sizes
    mem_B = Kt*padded_M
    mem_C = Nt*padded_M

    # We first estimate the memory so we can skip unnecessary computations
    upper_nnz = Nt*Kt*(density/100) # calculate the mean nnz
    upper_nnz -= upper_nnz*0.2 # Give some buffer
    mem_A_val = upper_nnz
    mem_A_colidx = upper_nnz
    mem_A_rowptr = Nt+1

    mem_estimate = 4*(mem_B+mem_C+mem_A_val+mem_A_rowptr+mem_A_colidx)
    if(mem_estimate > MEM-RESERVED):
        return mem_estimate

    # If estimated memory is within range, we do the actual computation
    A_val_len, A_colidx_len, A_rowptr_len = get_nnz_csr(int(Nt*height), int(Kt*width), height, width, density)

    # Use actual sizes
    mem_A_val = A_val_len
    mem_A_colidx = A_colidx_len
    mem_A_rowptr = A_rowptr_len

    return 4*(mem_B+mem_C+mem_A_val+mem_A_rowptr+mem_A_colidx)

def get_nnz_coo(N, K, height, width, density):
    """Gets A_len from a COO formatted matrix.

    Parameters
    ----------
    N: row dimension
    K: column dimension
    height: grid height
    width: grid width
    density: density of the matrix A

    Returns
    -------
    A_len for the submatrices defined by N x K and height x width PEs.
    """

    # Generate the matrix format
    retrieve_params = subprocess.check_output(f"./a.out {N} {K} {density} {height} {width} 2", shell=True, universal_newlines=True)

    # Process the output of the second file
    lines = retrieve_params.splitlines()

    return int(lines[0])

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

    # Get B and C sizes
    mem_B = Kt*padded_M
    mem_C = Nt*padded_M

    # We first estimate the memory so we can skip unnecessary computations
    upper_nnz = Nt*Kt*(density/100) # calculate the mean nnz
    upper_nnz -= upper_nnz*0.2 # Give some buffer
    mem_A_val = upper_nnz
    mem_A_x = upper_nnz
    mem_A_y = upper_nnz

    mem_estimate = 4*(mem_B+mem_C+mem_A_val+mem_A_x+mem_A_y)
    if(mem_estimate > MEM-RESERVED):
        return mem_estimate

    # If estimated memory is within range, we do the actual computation
    A_len = get_nnz_coo(int(Nt*height), int(Kt*width), height, width, density)

    # Use actual A_len
    mem_A_val = A_len
    mem_A_x = A_len
    mem_A_y = A_len

    return 4*(mem_B+mem_C+mem_A_val+mem_A_x+mem_A_y)

def get_nnz_ellpack(N, K, height, width, density):
    """Gets A_len from a ELLPACK formatted matrix.

    Parameters
    ----------
    N: row dimension
    K: column dimension
    height: grid height
    width: grid width
    density: density of the matrix A

    Returns
    -------
    A_len for the submatrices defined by N x K and height x width PEs.
    """

    # Generate the matrix format
    retrieve_params = subprocess.check_output(f"./a.out {N} {K} {density} {height} {width} 3", shell=True, universal_newlines=True)

    # Process the output of the second file
    lines = retrieve_params.splitlines()

    return int(lines[0])

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

    # Get B and C sizes
    mem_B = Kt*padded_M
    mem_C = Nt*padded_M

    # We first estimate the memory so we can skip unnecessary computations
    upper_nnz = Kt*(density/100) # calculate the mean nnz IN ONE ROW!
    upper_nnz -= upper_nnz*0.2 # Give some buffer
    mem_A_val = Nt*upper_nnz
    mem_A_indices = Nt*upper_nnz

    mem_estimate = 4*(mem_B+mem_C+mem_A_val+mem_A_indices)
    if(mem_estimate > MEM-RESERVED):
        return mem_estimate

    # If estimated memory is within range, we do the actual computation
    A_len = get_nnz_ellpack(int(Nt*height), int(Kt*width), height, width, density)
    
    # Use actual A_len
    mem_A_val = Nt*A_len
    mem_A_indices = Nt*A_len

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

def main():
    density_list = [5, 10, 20, 30]
    NK_list = [(768, 768) , (3072, 768), (768, 3072), (1024,1024), (4096, 1024), (1024, 4096)]

    f_out = []

    for density in tqdm(density_list):
        for (N,K) in tqdm(NK_list, leave=False):
            output = []

            grid_height_list = [i for i in range(1, AVAIL_HEIGHT) if N % i == 0]
            grid_width_list = [i for i in range(1, AVAIL_WIDTH) if K % i == 0]
            zipped = list(itertools.product(grid_height_list,grid_width_list))

            for M in tqdm([32, 64, 128, 256, 512, 768, 1024, 2048, 4096], leave=False):

                # [IMPORTANT]: Change which format is used here:
                # Options:
                # memory_used_coo
                # memory_used_csc
                # memory_used_csr
                # memory_used_ellpack
                # memory_used_gemm
                mem_used = [memory_used_coo(int(N/h), int(K/w), M, density, w, h) for (h,w) in zipped]

                grid_height_list = [x[0] for x in zipped]
                grid_width_list = [x[1] for x in zipped]

                # Get configs that fit in a PE
                configs = [(mem_used[i], grid_height_list[i], grid_width_list[i], (N/grid_height_list[i])*(K/grid_width_list[i]), int(M)) for i in range(len(grid_width_list)) if mem_used[i] < MEM-RESERVED]
                
                if(len(configs) == 0):
                    continue
                best_config = sorted(configs, key=itemgetter(0))[-1]
                mem_max = best_config[0]

                # Get all configs that are within 5% range
                for config in configs:
                    mem = config[0]
                    if mem_max - (mem_max*0.05) < mem:
                        output.append((mem, config[1], config[2], config[3], config[4]))


            # Sort by Nt x Kt first (4th element) and extract highest amount
            # max_ntkt = sorted(output, key=itemgetter(3))[-1][3]
            # Extract all configs with high enough non-zeroes
            BOUND = 64
            dens_perc = density/100
            #print(output)
            ntkt_config = [c for c in output if BOUND<=(c[3]*dens_perc)]
            #print(" ")
            #print(len(ntkt_config))

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
            _, h, w, _, m = final_output[0]
            f_out.append([N, K, density, h, w, m])

    # Print final output
    print(f"A_heights=({' '.join([str(x[0]) for x in f_out])})")
    print(f"A_widths=({' '.join([str(x[1]) for x in f_out])})")
    print(f"A_densities=({' '.join([str(x[2]) for x in f_out])})")
    print(f"grid_h=({' '.join([str(x[3]) for x in f_out])})")
    print(f"grid_w=({' '.join([str(x[4]) for x in f_out])})")
    print(f"M_w=({' '.join([str(x[5]) for x in f_out])})")

if __name__ == "__main__":
    main()






