I collection of python scripts for plotting/extracting data from LTSpice log files. I left a few examples for context

to plot in 3d against 2 step'ed parameters open *plot3d_2step.py*, change the axis scales (search xscale), and run

to get a table (spreadsheet) of step and meas data run maketable.py

any other formats are likely to be left out as LTSpice already does a good job plotting these

basic use to get data:
```
from parse_ltspice_log import *
logfilename, meas_lists, meas_lists_names, step_lists, step_lists_names = lts_log_Parser()
```
logfilename: string

meas_lists: list of lists containing each measurement (only the primary datapoint, others i.e. trigger times are not recorded)

meas_lists_names: a list of each measurement's name in the same order as meas_lists

step_lists: a list of lists containing each stepped parameters values
step_lists_names: a list of each stepped parameter's name in the same order as step_lists


made this for an intro to electronics lab where I went on several tangents and ended up trying to find out what capacitors I should use with the secondary of a broken transformer to make a pi filter only to realize it wasn't easy to just run a handful of simulations and look at the output then more rabbit holes of .meas and plotting and here we are..... I may have gotten sidetracked
