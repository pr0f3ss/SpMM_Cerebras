# ProjectCerebras'
This repository contains the relevant code and files for the Distributed Labs project of Emir Derouiche and Filip Dobrosavljevic (Fall/Winter 2022 Semester).  

## Links
- [Video playlist on Cerebras Hardware](https://www.youtube.com/playlist?list=PLCiO1ulV2l-buO1QruG7bGkmREvhXDckc)
- [Computational fluid dynamics acceleration with Cerebras video](https://www.youtube.com/watch?v=AZEoSkbPsZI)
- [Cerebras SDK overview video](https://www.youtube.com/watch?v=ZXJzS_LHxcQ)
- [PDF Technical Overview of Cerebras SDK](https://f.hubspotusercontent30.net/hubfs/8968533/Cerebras%20SDK%20Technical%20Overview%20White%20Paper.pdf)
- [GNN paper](https://arxiv.org/abs/2205.09702)


## Organization
- `summaries`: contains summaries of reviewed material
- `documents`: research papers and other relevant pdf files
- `src`: source files
- `src/benchmarks`: source files regarding benchmarking
- `test`: test input and output files
- `lib`: relevant libraries
- `plots`: final plots and figures of conducted benchmarking

## Convertor.c
To generate a random height x width matrix with a specific density in the desired format use:

`./a.out A_height A_width A_density Py Px Format`

`A_height`: Height dimension of A (rows, N)
`A_width`: Width dimension of A (columns, K)
`A_density`: supplied as percentage
`Py`: The PE height dimension (how many PE rows exist)
`Px`: The PE height dimension (how many PE columns exist)
`Format`: 0: CSC, 1: CSR, 2: Custom

This will generate 4 files with prefix `tmp`.

## add_padding.py
To add a padding to the converted files with filename prefix `tmp`, use:

`python3 add_padding.py Format`

`Format`: 0: CSC, 1: CSR, 2: Custom

By default, it adds a suffix `_pad` to the new files.


## Workflow
The general workflow to get the simulator to run is described in the following.

- Use `src/sparse_format_convertors/convertor.c` to generate a matrix and its corresponding files for the desired input format.
- Use `src/sparse_format_convertors/add_padding.py` to add padding to the generated input files. By default, it adds a suffix `_pad` to the new files.
- Move the input files to the local simulator example `test_vectors` folder. 
- Edit `commands.sh` such that all parameters are adjusted to the new input files. For example, for the grid CSC simulator run this includes Nt, Kt, M, the A array lengths and the A_prefix name (which is the prefix used before the suffix 'col_ptr', 'row_ptr' and 'val'). Depending on the format, different parameters have to be supplied.

## Automated testing
To conveniently test all working implementations, one can use `src/automated_testing/full_test.sh`. The specific parameters can be supplied to in `full_test.sh` as an array. 

Note: Before `full_test.sh` can be used, compile `src/sparse_format_convertors/convertor.c` with gcc in `src/sparse_format_convertors/`.
