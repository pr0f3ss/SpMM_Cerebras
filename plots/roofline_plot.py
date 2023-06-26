# @file
# @brief This python script plots the rooflines according to the data from "../benchmarks".

import numpy as np
import matplotlib.pyplot as plt
from numpy import genfromtxt
import seaborn as sns
import argparse
import os
import pandas as pd


def main():
    # Set plot data
    height = 768
    width = 768
    density = 20

    # set general plot information
    type = "apwp"
    figtext = "Cerebras WSE-2"
    xlabel = "I(n) [flops/byte]"
    ylabel = "P(n) [flops/cycle]"
    title = f"Performance of SpMM and GeMM implementations with {100 - density}% sparsity."
    savefile = f"figures/roofline_{100-density}.png"
    ax = plt.gca()

    # initialize plot
    plt.xlabel(xlabel, loc="center")
    plt.ylabel(ylabel, rotation="horizontal", labelpad=0, alpha=0.75, loc="top")
    ax.yaxis.set_label_coords(0.1, 1.015)
    plt.figtext(0.73, 0.895, figtext, alpha=0.75)
    plt.title(title, y=1.06, loc="center")

    # retrieve dataset
    filepath_gemm = "../benchmarks/GEMM_benchmark.csv"
    filepath_coo = "../benchmarks/COO_benchmark.csv"
    filepath_csc = "../benchmarks/CSC_benchmark.csv"
    filepath_csr = "../benchmarks/CSR_benchmark.csv"
    filepath_ellpack = "../benchmarks/ELLPACK_benchmark.csv"

    df_gemm  = pd.read_csv(filepath_gemm)
    df_gemm = df_gemm[df_gemm["density"] == 100]

    df_coo = pd.read_csv(filepath_coo)
    df_coo = df_coo[df_coo["density"] == density]

    df_csc = pd.read_csv(filepath_csc)
    df_csc = df_csc[df_csc["density"] == density]

    df_csr = pd.read_csv(filepath_csr)
    df_csr = df_csr[df_csr["density"] == density]

    df_ellpack = pd.read_csv(filepath_ellpack) 
    df_ellpack = df_ellpack[df_ellpack["density"] == density]

    # GEMM data
    gemm_flops = df_gemm["total_flops"]
    gemm_bytes = df_gemm["total_absolute_accesses"]
    gemm_cycles = df_gemm["avg_cycles"]*df_gemm["width"]*df_gemm["height"]

    x1 = gemm_flops / gemm_bytes
    y1 = gemm_flops / gemm_cycles

    # COO data
    coo_flops = df_coo["total_flops"]
    coo_bytes = df_coo["total_absolute_accesses"]
    coo_cycles = df_coo["avg_cycles"]*df_coo["width"]*df_coo["height"]

    x2 = coo_flops / coo_bytes
    y2 = coo_flops / coo_cycles

    print(x2)
    print(y2)

    # CSC data
    csc_flops = df_csc["total_flops"]
    csc_bytes = df_csc["total_absolute_accesses"]
    csc_cycles = df_csc["avg_cycles"]*df_csc["width"]*df_csc["height"]

    x3 = csc_flops / csc_bytes
    y3 = csc_flops / csc_cycles

    # CSR data
    csr_flops = df_csr["total_flops"]
    csr_bytes = df_csr["total_absolute_accesses"]
    csr_cycles = df_csr["avg_cycles"]*df_csr["width"]*df_csr["height"]

    x4 = csr_flops / csr_bytes
    y4 = csr_flops / csr_cycles

    # Ellpack data
    ellpack_flops = df_ellpack["total_flops"]
    ellpack_bytes = df_ellpack["total_absolute_accesses"]
    ellpack_cycles = df_ellpack["avg_cycles"]*df_ellpack["width"]*df_ellpack["height"]

    x5 = ellpack_flops / ellpack_bytes
    y5 = ellpack_flops / ellpack_cycles

    # # plot data
    fmt1 = "-v"
    fmt2 = "-v"
    fmt3 = "-v"
    fmt4 = "-v"
    fmt5 = "-v"

    plt.plot(x3, y3, fmt3, color="orangered", label=f"CSC")
    plt.plot(x4, y4, fmt4, color="forestgreen", label=f"CSR")
    plt.plot(x2, y2, fmt2, color="deeppink", label=f"COO")
    plt.plot(x1, y1, fmt1, color="darkorange", label=f"GeMM")
    plt.plot(x5, y5, fmt5, color="royalblue", label=f"Ellpack")

    plt.axhline(y=2, color='k', ls=':')
    plt.axvline(x=2/12, color='k', ls='--', alpha=0.6)
    
    plt.text(0.05, 0.95,'Peak Performance', color='k', fontdict={'size': 'smaller'},  transform=ax.transAxes)
    plt.text(0.1, 0.8,'Memory Bandwidth', color='k', fontdict={'size': 'smaller'},  transform=ax.transAxes, rotation=6.0)
    plt.text(0.835, 0.35,'Memory/Compute Bound', color='k', fontdict={'size': 'smaller'},  transform=ax.transAxes, rotation=270.0)

    # Draw mem line
    mem_x = np.linspace(0.15, 0.17, 200)
    mem_y = 12.0*mem_x
    plt.plot(mem_x, mem_y, color='k', alpha=0.6)

    # Draw legend
    plt.legend(loc=(1.04, 0.65))
    plt.grid()

    # Set limits
    plt.xlim([0.15, 0.17])
    plt.ylim([0.425, 2.1])

    # save
    plt.savefig(savefile, bbox_inches='tight', format='png')
    #plt.show()

if __name__ == "__main__":
    main()
