A_heights=(768 768 768 768 768 4096 4096 4096 4096 4096)
A_widths=(4096 4096 4096 4096 4096 4096 4096 4096 4096 4096)
A_densities=(5 10 15 20 30 5 10 15 20 30)
# 4*768*4096*3 = 37.74 MB
# 37.74 MB / (64*64) = 9.2 KB
# 4*4096*4096*3 = 201.33 MB
# 201.33 MB / (128*128) = 12.19 KB
grid_h=(64 64 64 64 64 128 128 128 128 128)
grid_w=(64 64 64 64 64 128 128 128 128 128)

implementations=("CSC" "CSR" "COO" "ELLPACK")

implementations_len=${#implementations[@]}
testlen=${#A_heights[@]}

for (( i=0; i<${testlen}; i++ ));
do
    for (( j=0; j<implementations_len; j++ ));
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