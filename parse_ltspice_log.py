import numpy as np
from os import path as os_path
from tkinter import filedialog

def open_file_dialog():
    file_path = filedialog.askopenfilename(filetypes=[("Log files", "*.log")])
    if file_path:print("Selected file:", file_path)
    else:print("No file selected.")
    return file_path

#make a class to keep track of the data? TODO
def lts_log_Parser(numSteps=-1, logFilePath = '', returnFileName=False, returnFilePath=False,):
    '''parse an LTSpice Log file line by line for step and meas data. all parameters are optional
    
    numSteps: specify how many step'd parameters are expected
    logFilePath: if not given will open a dialog 

    returns fileName, filepath, meas_lists, meas_lists_names, step_lists, step_lists_names
    '''
    
    if logFilePath == '': logFilePath = open_file_dialog()   #if no file path is given
    logFileName = os_path.basename(logFilePath)
    
    meas_lists, meas_lists_names, step_lists, step_lists_names = log_parser_helper(logFilePath)
    
    #check number of step'd parameters
    if (numSteps > 0) and len(step_lists_names) != numSteps:raise AttributeError(f'encountered {len(step_lists_names)} sted\'ed parameters in log file, was expecting {numSteps}')

    #TODO handle returning name and path
    if returnFileName: return logFileName, meas_lists, meas_lists_names, step_lists, step_lists_names
    return meas_lists, meas_lists_names, step_lists, step_lists_names



def log_parser_helper(fname):
    """ A generator function that runs log_parse_line, line by line, 
    return meas_lists, meas_lists_names, step_lists, step_lists_names"""
    
    step_lists_names = []   # Initialize a list to hold step'd parameter names
    step_lists = []         # Initialize a list to hold lists of step'd parameter values (independent)
    current_meas_list = []  # Initialize a list to hold current .meas values
    meas_lists_names = []   # Initialize a list to hold names of .meas lists
    meas_lists = []         # Initialize a list to hold all .meas lists ( dependent, yay 5*5000 array)
    
    with open(fname, mode='r') as log_file: #generator function
        for line in log_file:
            
            current_meas_list, meas_lists, meas_lists_names, step_lists, step_lists_names = log_parse_line(line, current_meas_list, meas_lists, meas_lists_names, step_lists, step_lists_names)            #do all the work
        
        if current_meas_list:meas_lists.append(current_meas_list)# append the last list to meas_lists (if it's not empty)
    return meas_lists, meas_lists_names, step_lists, step_lists_names

def log_parse_line(linestr, current_meas_list, meas_lists, meas_lists_names, step_lists, step_lists_names):
    """ decide what to do with each line of the log file and append to lists for plotting """
    ###LTspice .meas log format###
    #header            (ignore)    has no  \t characters, start of doc
    #step data         (x y)       starts  ' .step <namex>=<val> <namey>=<val>'            check second (starts with .step), append to x and y lists
    #random sim data   (ignore)    has no  \t characters, i.e. temp, method
    #measurement name  (z name)    starts  ' Measurement: <name>'                         check third, switch between z list
    #measurement format(ignore)    starts  '   step\t<type>(<net>)\t<parameter>...'
    #measurement data  (z value)   starts  '<whitespace><step>\t<val>\t<parameter>...'    check first (\t at index 6, doesn't start with  '   step'), append to current z list
    try:
        #measurement data
        if (linestr[6]=='\t') and ('step' not in linestr):
            current_meas_list.append(np.float64(linestr.split('\t')[1].strip()))
        
        #step data
        elif linestr.startswith(".step"):
            if not step_lists_names:
                step_lists_names = linestr[6:].replace('=',' ').split(' ')[::2] #if it hasn't been done already copy step'd parameter names into storage
                for i in range(len(step_lists_names)):step_lists.append([])     #and set the number of independent step'd parameters that will be stored
            
            for index, val in enumerate(linestr[6:].replace('=',' ').split(' ')[1::2]): step_lists[index].append(np.float64(val.strip())) #append step parameters into storage
        
        #new measurement/name
        elif linestr.startswith("Measurement:"):
            #print(linestr,'new measurement')
            meas_lists_names.append(linestr.split(":")[1].strip()) #copy measurement name into storage
            
            if current_meas_list:                    #if current list is NOT empty (skip first)
                meas_lists.append(current_meas_list)  #copy measurements into storage (makes a list of lists)
                current_meas_list = []               #reset current_meas_list for the new measurement

        return current_meas_list, meas_lists, meas_lists_names, step_lists, step_lists_names
    
    #no data recorded
    except (ValueError,IndexError) as e: return current_meas_list, meas_lists, meas_lists_names, step_lists, step_lists_names