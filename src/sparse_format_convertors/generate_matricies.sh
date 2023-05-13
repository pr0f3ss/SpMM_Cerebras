A_heights=(16)
A_widths=(16)
A_densities=(15)
grid_h=(2)
grid_w=(4)
M_w=(32)
implementations=("CSC" "CSR" "COO" "ELLPACK")

testlen=${#A_heights[@]}

for (( i=0; i<${testlen}; i++ ));
do
    for (( j=0; j<4; j++ ));
    do
        dir="${implementations[j]}_${A_heights[i]}x${A_widths[i]}_${A_densities[i]}"
        mkdir $dir
        mv a.out $dir
        mv add_padding.py $dir
        cd $dir
        ./a.out ${A_heights[i]} ${A_widths[i]} ${A_densities[i]} ${grid_h[i]} ${grid_w[i]} $j
        OUTPUT=($(python3 add_padding.py ${j}| tr -d '[],')) # Evaluate output from python script as an array of numbers
        mv a.out ..
        mv add_padding.py ..
        cd ..
    done
done