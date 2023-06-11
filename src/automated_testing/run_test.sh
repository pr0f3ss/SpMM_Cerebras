#!/usr/bin/env bash

set -e
set -x

A_height=$1
A_width=$2
A_density=$3
grid_height=$4
grid_width=$5
M_width=$6

# Initialize test directories
mkdir ../gemm/test_vectors
mkdir ../grid_csc/test_vectors
mkdir ../grid_csr/test_vectors
mkdir ../grid_coo/test_vectors
mkdir ../grid_ellpack/test_vectors

for i in 0 1 2 3
do
    cd ../sparse_format_convertors
    # Generate A matrix
    ./a.out $A_height $A_width $A_density $grid_height $grid_width $i
    OUTPUT=($(python3 add_padding.py ${i}| tr -d '[],')) # Evaluate output from python script as an array of numbers
    
    #SDK 0.6.0 requires fabrics dimensions: dim_x >= x + width + 3 + width-east-buf, dim_y >= y + height + 1.
    case $i in
    0)
        # Additionally test GEMM in here too
        val_len=${OUTPUT[2]} 
        row_idx_len=${OUTPUT[6]}
        col_ptr_len=${OUTPUT[10]}
        mv tmp_*_pad.csv ../grid_csc/test_vectors
        cp tmp.csv ../gemm/test_vectors
        mv tmp.csv ../grid_csc/test_vectors
        rm tmp*
        cd ../grid_csc

        cslc ./layout.csl --fabric-dims=$(($grid_width + 7)),$(($grid_height + 2)) --fabric-offsets=4,1 --params=width:$grid_width,height:$grid_height,Nt:$(($A_height / $grid_height)),Kt:$(($A_width / $grid_width)),M:$M_width,A_val_len:$val_len,A_rowidx_len:$row_idx_len,A_colptr_len:$col_ptr_len,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0
        cs_python run_memcpy.py --name out -N=$A_height -K=$A_width -M=$M_width -A_prefix="tmp" -width=$grid_width -height=$grid_height

        # remove CSC run
        rm simfab_traces/ -rf
        rm out/ -rf

        # Now test GEMM
        cd ../gemm
        cslc ./layout.csl --fabric-dims=$(($grid_width + 7)),$(($grid_height + 2)) --fabric-offsets=4,1 --params=width:$grid_width,height:$grid_height,Nt:$(($A_height / $grid_height)),Kt:$(($A_width / $grid_width)),M:$M_width,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0
        cs_python run_memcpy.py --name out -N=$A_height -K=$A_width -M=$M_width -A_prefix="tmp" -width=$grid_width -height=$grid_height

        # remove GEMM run
        rm simfab_traces/ -rf
        rm out/ -rf
        ;;

    1)  
        val_len=${OUTPUT[2]} 
        col_idx_len=${OUTPUT[6]}
        row_ptr_len=${OUTPUT[10]}
        mv tmp_*_pad.csv ../grid_csr/test_vectors
        mv tmp.csv ../grid_csr/test_vectors
        rm tmp*
        cd ../grid_csr

        cslc ./layout.csl --fabric-dims=$(($grid_width + 7)),$(($grid_height + 2)) --fabric-offsets=4,1 --params=width:$grid_width,height:$grid_height,Nt:$(($A_height / $grid_height)),Kt:$(($A_width / $grid_width)),M:$M_width,A_val_len:$val_len,A_colidx_len:$col_idx_len,A_rowptr_len:$row_ptr_len,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0
        cs_python run_memcpy.py --name out -N=$A_height -K=$A_width -M=$M_width -A_prefix="tmp" -width=$grid_width -height=$grid_height

        # remove run
        rm simfab_traces/ -rf
        rm out/ -rf
        ;;

    2)  
        val_len=${OUTPUT[2]} 
        col_len=${OUTPUT[6]}
        row_len=${OUTPUT[10]}
        mv tmp_*_pad.csv ../grid_coo/test_vectors
        mv tmp.csv ../grid_coo/test_vectors
        rm tmp*
        cd ../grid_coo

        cslc ./layout.csl --fabric-dims=$(($grid_width + 7)),$(($grid_height + 2)) --fabric-offsets=4,1 --params=width:$grid_width,height:$grid_height,Nt:$(($A_height / $grid_height)),Kt:$(($A_width / $grid_width)),M:$M_width,A_len:$(($val_len+1)),LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0
        cs_python run_memcpy.py --name out -N=$A_height -K=$A_width -M=$M_width -A_prefix="tmp" -width=$grid_width -height=$grid_height

        # remove run
        rm simfab_traces/ -rf
        rm out/ -rf
        ;;

    3)  
        val_len=${OUTPUT[2]} 
        mv tmp_*_pad.csv ../grid_ellpack/test_vectors
        mv tmp.csv ../grid_ellpack/test_vectors
        rm tmp*
        cd ../grid_ellpack

        cslc ./layout.csl --fabric-dims=$(($grid_width + 7)),$(($grid_height + 2)) --fabric-offsets=4,1 --params=width:$grid_width,height:$grid_height,Nt:$(($A_height / $grid_height)),Kt:$(($A_width / $grid_width)),M:$M_width,A_len:$val_len,LAUNCH_ID:4 -o=out --memcpy --channels=1 --width-west-buf=0 --width-east-buf=0
        cs_python run_memcpy.py --name out -N=$A_height -K=$A_width -M=$M_width -A_prefix="tmp" -width=$grid_width -height=$grid_height

        # remove run
        rm simfab_traces/ -rf
        rm out/ -rf
        ;;

    *)
        echo "Format specifier unknown."
        ;;
    esac
done

# Remove test directories
rm -rf ../gemm/test_vectors
rm -rf ../grid_csc/test_vectors
rm -rf ../grid_csr/test_vectors
rm -rf ../grid_coo/test_vectors
rm -rf ../grid_ellpack/test_vectors


