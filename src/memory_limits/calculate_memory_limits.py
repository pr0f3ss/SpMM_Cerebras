import numpy as np
import math
import matplotlib.pyplot as plt
import scipy.stats as stats
import xlsxwriter,datetime,os
import itertools
from matplotlib.font_manager import FontProperties

# Defines the memory available per PE
MEM = 48*1024
RESERVED = 8*1024 # Reserve 1/6 of actual memory for program, dsd buffers etc.
GUARANTEE = 0.99
AVAIL_HEIGHT = 996
AVAIL_WIDTH = 757

def find_upper_bound_nnz(Nt, Kt, density):
    """Calculates an upper bound of elements 'x' in a Nt x Kt submatrix generated with density 'd'
    The upper bound is guaranteed with probabilty at least 'GUARANTEE'

    Parameters
    ----------
    Nt: dimension Nt = N / grid_height
    Kt: dimension Kt = K / grid_width
    density: density of the matrix A

    Returns
    -------
    An upper bound (with probabilty 'GUARANTEE') of the elements inside a Nt x Kt submatrix with density 'd'.
    """

    d = density/100
    # Calculate the total number of elements in the matrix
    total_elements = Nt * Kt

    # Calculate the upper bound on the number of non-zero elements
    # Largest k such that P[X <= k] >= GUARANTEE
    k_upper = stats.binom.isf(1-GUARANTEE, total_elements, d)
    return int(k_upper)

def memory_used_coo(Nt, Kt, M, density):
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
    upper_nnz = find_upper_bound_nnz(Nt, Kt, density)

    # Calculate the number of 4 byte elements
    # Rest of buffers accounted for in reserved memory
    mem_B = Kt*padded_M
    mem_C = Nt*padded_M
    mem_A_val = upper_nnz
    mem_A_x = upper_nnz
    mem_A_y = upper_nnz

    return 4*(mem_B+mem_C+mem_A_val+mem_A_x+mem_A_y)

def memory_used_csr(Nt, Kt, M, density):
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
    upper_nnz = find_upper_bound_nnz(Nt, Kt, density)

    # Calculate the number of 4 byte elements
    # Rest of buffers accounted for in reserved memory
    mem_B = Kt*padded_M
    mem_C = Nt*padded_M
    mem_A_val = upper_nnz
    mem_A_rowptr = Nt+1
    mem_A_colidx = upper_nnz

    return 4*(mem_B+mem_C+mem_A_val+mem_A_rowptr+mem_A_colidx)

def memory_used_csc(Nt, Kt, M, density):
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
    upper_nnz = find_upper_bound_nnz(Nt, Kt, density)

    # Calculate the number of 4 byte elements
    # Rest of buffers accounted for in reserved memory
    mem_B = Kt*padded_M
    mem_C = Nt*padded_M
    mem_A_val = upper_nnz
    mem_A_rowidx = upper_nnz
    mem_A_colptr = Kt+1

    return 4*(mem_B+mem_C+mem_A_val+mem_A_rowidx+mem_A_colptr)

def memory_used_ellpack(Nt, Kt, M, density):
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
    upper_nnz = find_upper_bound_nnz(Nt, Kt, density)

    # Calculate the number of 4 byte elements
    # Rest of buffers accounted for in reserved memory
    mem_B = Kt*padded_M
    mem_C = Nt*padded_M
    mem_A_val = upper_nnz
    mem_A_indices = upper_nnz

    return 4*(mem_B+mem_C+mem_A_val+mem_A_indices)

def memory_used_gemm(Nt, Kt, M, density):
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

    # Calculate the number of 4 byte elements
    # Rest of buffers accounted for in reserved memory
    mem_B = Kt*padded_M
    mem_C = Nt*padded_M
    mem_A = Nt*Kt

    return 4*(mem_B+mem_C+mem_A)


M = 512
density = 10
N = 1024
K = 1024

grid_height_list = [i for i in range(1, AVAIL_HEIGHT) if N % i == 0]
grid_width_list = [i for i in range(1, AVAIL_WIDTH) if K % i == 0]

zipped = list(itertools.product(grid_height_list,grid_width_list))

mem_used = [memory_used_coo(int(N/h), int(K/w), M, density) for (h,w) in zipped]

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Create an new Excel file and add a worksheet.
workbook = xlsxwriter.Workbook(f'src/memory_limits/mem_sheets/mem_limit_M{M}_N{N}_K{K}_d{density}.xlsx', {'nan_inf_to_errors': True})
worksheet = workbook.add_worksheet()


# Widen the first column to make the text clearer.
worksheet.set_column('A:A', 20)

# Add a bold format to use to highlight cells.
bold = workbook.add_format({'bold': True})

worksheet.write(0,0, 'Grid height/width', bold)

it = 0
for j,x in enumerate(grid_height_list):
    worksheet.write(j+1,0, str(x), bold)
    for i,y in enumerate(grid_width_list):
        worksheet.write(0,i+1, y, bold)
        if(mem_used[it] <= MEM-RESERVED):
            worksheet.write(j+1,i+1, mem_used[it])
        it+=1

workbook.close()

grid_height_list = [x[0] for x in zipped]
grid_width_list = [x[1] for x in zipped]

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# plot
scatter_plot = plt.scatter(grid_height_list, grid_width_list, c=mem_used, cmap='hot', edgecolors='black')

# Add a color bar for the heatmap
scatter_plot.set_clim(vmin=0, vmax=MEM-RESERVED)
cbar = plt.colorbar(scatter_plot, format='%.0f')
cbar.set_label('Memory used in Bytes')

# Set the axis labels
plt.xlabel('Grid height')
plt.ylabel('Grid width')

plt.xscale('log')
plt.yscale('log')

# Set ticks
plt.xticks(grid_height_list, grid_height_list)
plt.yticks(grid_width_list, grid_width_list)

# Create a FontProperties object with normal font weight
font_normal = FontProperties(weight='normal')

# Set the tick labels font properties to normal weight
plt.xticks(fontproperties=font_normal)
plt.yticks(fontproperties=font_normal)

# Set the title of the plot
titlestr=f"M = {M}, Density = {density}, NxK = {N}x{K}"
plt.title(titlestr)
plt.show()




