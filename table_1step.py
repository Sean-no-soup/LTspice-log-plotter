from openpyxl import Workbook
import numpy as np

from parse_ltspice_log import *
meas_lists, meas_lists_names, step_lists, step_lists_names = lts_log_Parser(2, returnFileName=True)

lol this is so unfinished but I want to go to sleep 

#TODO check num steps

#convert to table friendly format, these can usually be graphed no problem
wb = Workbook()
ws = wb.active
#[[ , , , ],\ lines up with cells in spreadsheet
# [ , , , ],\ make an array and transpose to be spreadsheet friendly
# [ , , , ],] first of each row will start as the name/title, step in first row
for each meas
data = np.append(title, data)

https://numpy.org/doc/stable/reference/generated/numpy.concatenate.html
https://numpy.org/doc/stable/reference/generated/numpy.transpose.html

for row in treeData:
    ws.append(row)
    
#does this just update the file as it appends?
print()#print
