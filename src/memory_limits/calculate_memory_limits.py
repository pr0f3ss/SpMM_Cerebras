import numpy as np

import xlsxwriter,datetime,os

# Defines the memory available per PE
MEM = 48*1024


def memory_used_pe(y, m, max_pe):
    """Calculates the memory that is used per PE when using the grid CSC/R or custom format

    Parameters
    ----------
    y: dimension Nt/Kt
    m: dimension M 
    max_pe: the number of non-zero elements that will be in the y*y PE grid holding A (0 <= max_pe <= y*y)

    Returns
    -------
    Memory in bytes being used per PE
    """
    return 4*y*m + 4*2*y*m + 4*3*max_pe

# Create an new Excel file and add a worksheet.
workbook = xlsxwriter.Workbook('mem_limits.xlsx', {'nan_inf_to_errors': True})
worksheet = workbook.add_worksheet()


# Widen the first column to make the text clearer.
worksheet.set_column('A:A', 20)


# Add a bold format to use to highlight cells.
bold = workbook.add_format({'bold': True})

worksheet.write(0,0, 'M \ y (= Kt/Nt)', bold)

M_list = [32,64,128]
y_list = [i for i in range(20,240)]

for j,m in enumerate(M_list):

    worksheet.write(j+1,0, str(m), bold)


    for i,y in enumerate(y_list):
        worksheet.write(0,i+1, y, bold)

        search = memory_used_pe(y, m, y*y/5)

        if(MEM >= search):
            worksheet.write(j+1,i+1, search)

workbook.close()
