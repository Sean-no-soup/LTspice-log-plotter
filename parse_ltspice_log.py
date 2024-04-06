import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoLocator

def log_parser(fname):
    """ A generator function that runs log_parse_line line by line"""
    global current_meas_list, meas_lists, meas_lists_names, step_lists, step_lists_names
    step_lists_names = []      # Initialize a list to hold step'd parameter names
    step_lists = []      # Initialize a list to hold lists of step'd parameter values (independent)
    current_meas_list = []    # Initialize a list to hold current .meas values
    meas_lists_names = [] # Initialize a list to hold names of .meas lists
    meas_lists = []       # Initialize a list to hold all .meas lists ( dependent, yay 5*5000 array)
    
    with open(fname, mode='r') as log_file: #generator function
        for line in log_file:
            
            log_parse_line(line)            #do all the work
        
        if current_meas_list:meas_lists.append(current_meas_list)# append the last list to meas_lists (if it's not empty)
    
    return meas_lists, meas_lists_names, step_lists, step_lists_names

def log_parse_line(linestr):
    """ decide what to do with each line of the log file and append to lists for plotting """
    global current_meas_list, meas_lists, meas_lists_names, step_lists, step_lists_names
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

        return None
    
    except (ValueError,IndexError) as e: return None




if __name__ == "__main__":

    #look for a log file
    from tkinter import filedialog
    def open_file_dialog():
        file_path = filedialog.askopenfilename(filetypes=[("Log files", "*.log")])
        if file_path:print("Selected file:", file_path)
        else:print("No file selected.")
        return file_path
    logfilepath = open_file_dialog()

    #///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    #setup some plot stuff
    fig = plt.figure(figsize=(18, 12), dpi=80)
    ax = plt.axes(projection='3d')
    ax.set_proj_type('ortho')  #persp, ortho
    ax.set_title('generic toad')
    plt.subplots_adjust(bottom=0)
    xscale = 'linear'
    yscale = 'log'
    zscale = 'linear'
    #linear or log, matplotlib axis scale workaround (and it's been a known issue in 3d for 13+years)
    #///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def setup_grid(dataset,scale):
        if scale == 'log':return np.log10(dataset).reshape(xy_shape)
        elif scale == 'linear':return dataset.reshape(xy_shape)
        else: raise ValueError(f'invalid scale {scale}')

    def log_format_scientific(number):return np.format_float_scientific(10**number,precision=3,unique=True,trim='-',sign=False)
    def log_format_positional(number):return np.format_float_positional(10**number,precision=3,unique=True,trim='-',sign=False)
    def lin_format_scientific(number):return np.format_float_scientific(    number,precision=3,unique=True,trim='-',sign=False)
    def lin_format_positional(number):return np.format_float_positional(    number,precision=3,unique=True,trim='-',sign=False)
    def log_use_scientific(number):return (number <= -6 or number >= 6)
    def lin_use_scientific(number):return (number <= -(10**6) or number >= (10**6))

    def setup_ticks(axis):
        if   axis == 'x': idx = 0
        elif axis == 'y': idx = 1
        elif axis == 'z': idx = 2
        else: raise ValueError(f'invalid axis {axis}')
        scale = [xscale,yscale,zscale][idx]

        #reset ticks to automatic scaling
        getattr(ax, f'{axis}axis').set_major_locator(AutoLocator())

        #get the values as plotted (usually have good spacing)
        tick_locs = getattr(ax, f'get_{axis}ticks')()

        #fix workaround and put in float/scientific
        if scale == 'log':     tick_labels = [(log_format_scientific(loc) if log_use_scientific(loc) else log_format_positional(loc)) for loc in tick_locs]
        elif scale == 'linear':tick_labels = [(lin_format_scientific(loc) if lin_use_scientific(loc) else lin_format_positional(loc)) for loc in tick_locs]
        else: raise ValueError(f'invalid scale {scale}')

        #reset tick labels
        getattr(ax, f'set_{axis}ticks')(tick_locs) #makes matplotlib happy
        getattr(ax, f'set_{axis}ticklabels')(tick_labels)#,rotation=10)

    global meas_lists, meas_lists_names, step_lists, step_lists_names
    log_parser(logfilepath)
    x = np.array(step_lists[0])# Convert data to numpy array
    y = np.array(step_lists[1])# Convert data to numpy array
    z = np.array(meas_lists[0])# Convert data to numpy array, init with index 0
    xy_shape = (len(set(y)), len(set(x))) #number of unique elements in x and y axis

    wireframe = ax.plot_wireframe(setup_grid(x,xscale), setup_grid(y,yscale), setup_grid(z,zscale))

    ax.set_xlabel(step_lists_names[0])
    ax.set_ylabel(step_lists_names[1])
    ax.set_zlabel(meas_lists_names[0])
    setup_ticks('x')
    setup_ticks('y')
    setup_ticks('z')

    wireframe.remove()  # Reset wireframe, for some reason it plots smaller the first time ¯\_(ツ)_/¯
    wireframe = ax.plot_wireframe(setup_grid(x,xscale), setup_grid(y,yscale), setup_grid(z,zscale))

    # Function to update which meas data is shown
    def switch_meas_plot(new_index):
        global z, wireframe
        z = np.array(meas_lists[new_index])

        wireframe.remove()  # Remove old wireframe
        wireframe = ax.plot_wireframe(setup_grid(x,xscale), setup_grid(y,yscale), setup_grid(z,zscale)) # Create new wireframe

        ax.set_zlabel(meas_lists_names[new_index])

        #ax.zaxis.set_major_locator(AutoLocator())
        setup_ticks('z')

        plt.draw()

    # Add a button to cycle between datasets
    global current_index
    current_index = 0
    def on_button_click(event):
        global current_index
        current_index += 1
        switch_meas_plot((current_index) % len(meas_lists_names))
    button = plt.Button(plt.axes([0.8, 0.05, 0.1, 0.075]), 'Switch')
    button.on_clicked(on_button_click)

    plt.show()