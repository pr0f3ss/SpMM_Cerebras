# This file verifies the memory limits for each of the sparse grid formats
# It assumes the following textfile name specifier: FORMAT_params.txt\

from calculate_memory_limits import *

def verify_mem(filename):
    # Read the file and parse the arrays
    arrays = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            array_name, array_values = line.split('=(')
            array_values = [int(value) for value in array_values.rstrip(')').split()]
            arrays[array_name] = array_values

    num_checks = len(arrays["A_heights"])
    for i in range(num_checks):
        # Retrieve data first
        Nt = int( arrays["A_heights"][i] / arrays["grid_h"][i] )
        Kt = int( arrays["A_widths"][i] / arrays["grid_w"][i] )
        M_w = arrays["M_w"][i]
        density = arrays["A_densities"][i]
        width = arrays["grid_w"][i]
        height = arrays["grid_h"][i]

        # Use memory check functions to verify if they allocate too much
        if(filename == "GEMM_params.txt"):
            assert(memory_used_gemm(Nt, Kt, M_w, density, width, height) <= MEM - RESERVED)   
        elif(filename == "COO_params.txt"):
            assert(memory_used_coo(Nt, Kt, M_w, density, width, height) <= MEM - RESERVED)
        elif(filename == "CSC_params.txt"):
            assert(memory_used_csc(Nt, Kt, M_w, density, width, height) <= MEM - RESERVED)
        elif(filename == "CSR_params.txt"):
            assert(memory_used_csr(Nt, Kt, M_w, density, width, height) <= MEM - RESERVED)
        elif(filename == "ELLPACK_params.txt"):
            assert(memory_used_ellpack(Nt, Kt, M_w, density, width, height) <= MEM - RESERVED)
        else:
            assert()

    print(f"[!] {filename} verified and correct!")


def main():
    filenames = ["GEMM_params.txt", "COO_params.txt", "CSC_params.txt", "CSR_params.txt", "ELLPACK_params.txt"]
    for file in filenames:
        verify_mem(file)

if __name__ == "__main__":
    main()
