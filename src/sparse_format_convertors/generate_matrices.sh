#!/usr/bin/env bash

implementations=("CSC" "CSR" "COO" "ELLPACK" "GEMM")

# CSC
source ../memory_limits/CSC_params.txt
testlen=${#A_heights[@]}

for (( i=0; i<${testlen}; i++ ));
do
    dir="${implementations[0]}_${A_heights[i]}x${A_widths[i]}_${A_densities[i]}"
    mkdir $dir
    ./a.out ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} 0
    OUTPUT=($(python3 add_padding.py 0 | tr -d '[],')) # Evaluate output from python script as an array of numbers
    mv tmp* $dir
    val_len=${OUTPUT[2]} 
    row_idx_len=${OUTPUT[6]}
    col_ptr_len=${OUTPUT[10]}
    echo $val_len >> out.txt
    echo $row_idx_len >> out.txt
    echo $col_ptr_len >> out.txt
    echo "" >> out.txt
    mv out.txt $dir
    # cp to Gemm implementation
    cp -r $dir "../gemm_padshift"
    mv $dir "../grid_csc_padshift"
done

# CSR
source ../memory_limits/CSR_params.txt
testlen=${#A_heights[@]}

for (( i=0; i<${testlen}; i++ ));
do
    dir="${implementations[1]}_${A_heights[i]}x${A_widths[i]}_${A_densities[i]}"
    mkdir $dir
    ./a.out ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} 1
    OUTPUT=($(python3 add_padding.py 1 | tr -d '[],')) # Evaluate output from python script as an array of numbers
    mv tmp* $dir
    val_len=${OUTPUT[2]} 
    col_idx_len=${OUTPUT[6]}
    row_ptr_len=${OUTPUT[10]}
    echo $val_len >> out.txt
    echo $col_idx_len >> out.txt
    echo $row_ptr_len >> out.txt
    echo "" >> out.txt
    mv out.txt $dir
    mv $dir "../grid_csr_padshift"
done

# COO
source ../memory_limits/COO_params.txt
testlen=${#A_heights[@]}

for (( i=0; i<${testlen}; i++ ));
do
    dir="${implementations[2]}_${A_heights[i]}x${A_widths[i]}_${A_densities[i]}"
    mkdir $dir
    ./a.out ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} 2
    OUTPUT=($(python3 add_padding.py 2 | tr -d '[],')) # Evaluate output from python script as an array of numbers
    mv tmp* $dir 
    val_len=${OUTPUT[2]} 
    col_len=${OUTPUT[5]}
    row_len=${OUTPUT[8]}
    echo $val_len >> out.txt
    echo $col_len >> out.txt
    echo $row_len >> out.txt
    echo "" >> out.txt
    mv out.txt $dir
    mv $dir "../grid_custom_padshift"
done

# ELLPACK
source ../memory_limits/ELLPACK_params.txt
testlen=${#A_heights[@]}

for (( i=0; i<${testlen}; i++ ));
do
    dir="${implementations[3]}_${A_heights[i]}x${A_widths[i]}_${A_densities[i]}"
    mkdir $dir
    ./a.out ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} 3
    OUTPUT=($(python3 add_padding.py 3 | tr -d '[],')) # Evaluate output from python script as an array of numbers
    mv tmp* $dir 
    A_len=${OUTPUT[2]}
    echo $A_len >> out.txt
    echo "" >> out.txt
    mv out.txt $dir
    mv $dir "../grid_ellpack_padshift"
done
