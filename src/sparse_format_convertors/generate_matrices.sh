A_heights=(768 3072 768 1024 4096 1024)
A_widths=(768 768 3072 1024 1024 4096)
A_densities=(20 20 20 20 20 20)
grid_h=(16 24 16 8 32 128)
grid_w=(6 16 24 128 128 32)
M_w=(32 32 32 64 64 64)

implementations=("CSC" "CSR" "COO" "ELLPACK")

implementations_len=${#implementations[@]}
testlen=${#A_heights[@]}

for (( i=0; i<${testlen}; i++ ));
do
    for (( j=0; j<implementations_len; j++ ));
    do
        dir="${implementations[j]}_${A_heights[i]}x${A_widths[i]}_${A_densities[i]}"
        mkdir $dir
        ./a.out ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} $j
        OUTPUT=($(python3 add_padding.py ${j}| tr -d '[],')) # Evaluate output from python script as an array of numbers
        mv tmp* $dir
        case $j in
        0)
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
            ;;
        1)  
            val_len=${OUTPUT[2]} 
            col_idx_len=${OUTPUT[6]}
            row_ptr_len=${OUTPUT[10]}
            echo $val_len >> out.txt
            echo $col_idx_len >> out.txt
            echo $row_ptr_len >> out.txt
            echo "" >> out.txt
            mv out.txt $dir
            mv $dir "../grid_csr_padshift"
            ;;
        2)  
            val_len=${OUTPUT[2]} 
            col_len=${OUTPUT[5]}
            row_len=${OUTPUT[8]}
            echo $val_len >> out.txt
            echo $col_len >> out.txt
            echo $row_len >> out.txt
            echo "" >> out.txt
            mv out.txt $dir
            mv $dir "../grid_custom_padshift"
            ;;
        3)
            A_len=${OUTPUT[2]}
            echo $A_len >> out.txt
            echo "" >> out.txt
            mv out.txt $dir
            mv $dir "../grid_ellpack_padshift"
            ;;
        *)
            echo "Format specifier unknown."
            ;;
        esac
    done
done