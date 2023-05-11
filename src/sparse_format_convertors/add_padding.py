# This python file defines functions that automatically pad the grid/custom format and output its corresponding lengths in STDOUT

import numpy as np
import pandas as pd
import fileinput
from sys import argv

def col_is_nan(s):
    """Returns whether array-like object s is all NaN

    Parameters
    ----------
    s: array-like object 

    Returns
    -------
    True if all entries in s are NaN
    """
    a = s.to_numpy()
    return np.isnan(a).all()

def pad_file(input_filename, output_filename, replace=-1, dtype=int):
    """Pads the input file with replace characters at NaN positions and writes it to a new file 'output_filename'

    Parameters
    ----------
    input_filename: filename of the input matrix
    output_filename: filename of the output matrix
    replace (optional): number to replace it with
    dtype (optional): data type of output matrix

    Returns
    -------
    Prints the padded column length of the output file
    """
    with open(input_filename, 'r') as temp_f:
        # get No of columns in each line
        col_count = [ len(l.split(",")) for l in temp_f.readlines() ]

    length = max(col_count)
    column_names = [i for i in range(0, max(col_count))]

    df = pd.read_csv(input_filename, delimiter=',', header=None, names=column_names, skip_blank_lines=False)
    
    if(col_is_nan(df[length-1])):
        length = length - 1
        df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)

    print(length)
        
    df = df.replace(np.nan,replace)

    df = df.astype(dtype)

    df.to_csv(output_filename, index=False, header=False)


def pad_csc_grid(prefix, replace=-1):
    """Takes the prefix of a grid CSC formatted matrix and pads NaN entries with replace

    Parameters
    ----------
    prefix: prefix of the filenames of a CSC formatted matrix
    replace (optional): number to replace it with

    Returns
    -------
    Three files that have the padded grid CSV format
    """
    print("Value length:")
    pad_file(prefix+"_val.csv", prefix+"_val_pad.csv", dtype=float)

    print("Row index length:")
    pad_file(prefix+"_row_idx.csv", prefix+"_row_idx_pad.csv", dtype=int)

    print("Column pointer length:")
    pad_file(prefix+"_col_ptr.csv", prefix+"_col_ptr_pad.csv", dtype=int)

def pad_csr_grid(prefix, replace=-1):
    """Takes the prefix of a grid CSR formatted matrix and pads NaN entries with replace

    Parameters
    ----------
    prefix: prefix of the filenames of a CSR formatted matrix
    replace (optional): number to replace it with

    Returns
    -------
    Three files that have the padded grid CSV format
    """
    print("Value length:")
    pad_file(prefix+"_val.csv", prefix+"_val_pad.csv", dtype=float)

    print("Column index length:")
    pad_file(prefix+"_col_idx.csv", prefix+"_col_idx_pad.csv", dtype=int)

    print("Row pointer length:")
    pad_file(prefix+"_row_ptr.csv", prefix+"_row_ptr_pad.csv", dtype=int)

def pad_custom_grid(prefix, replace=-1):
    """Takes the prefix of a grid custom formatted matrix and pads NaN entries with replace

    Parameters
    ----------
    prefix: prefix of the filenames of a custom grid formatted matrix
    replace (optional): number to replace it with

    Returns
    -------
    Three files that have the padded grid CSV format
    """
    print("Value length:")
    pad_file(prefix+"_val.csv", prefix+"_val_pad.csv", dtype=float)

    print("Column length:")
    pad_file(prefix+"_x.csv", prefix+"_x_pad.csv", dtype=int)

    print("Row length:")
    pad_file(prefix+"_y.csv", prefix+"_y_pad.csv", dtype=int)

def pad_ellpack_grid(prefix, replace=-1):
    """Takes the prefix of a grid ellpack formatted matrix and pads NaN entries with replace

    Parameters
    ----------
    prefix: prefix of the filenames of a custom grid formatted matrix
    replace (optional): number to replace it with

    Returns
    -------
    Two files that have the padded grid CSV format
    """
    print("Value length:")
    pad_file(prefix+"_val.csv", prefix+"_val_pad.csv", dtype=float)

    print("Indices length:")
    pad_file(prefix+"_indices.csv", prefix+"_indices_pad.csv", dtype=int)
    
def main():
    prefix = "tmp"
    fmt_type = int(argv[1])
    if(fmt_type == 0):
        pad_csc_grid(prefix)
        
    elif(fmt_type == 1):
        pad_csr_grid(prefix)
        
    elif(fmt_type == 2):
        pad_custom_grid(prefix)
    
    elif(fmt_type == 3):
        pad_ellpack_grid(prefix)
        
    else:
        print("Incorrect format type. Did not add padded arrays.")

if __name__=="__main__":
    main()