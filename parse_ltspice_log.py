import sys
import numpy as np
import matplotlib.pyplot as plt

def log_parser(fname):
    """ A generator function that runs log_parse_line line by line"""
    global current_list, all_lists, all_lists_names, step_lists, step_names
    step_names = []      # Initialize a list to hold step'd parameter names
    step_lists = []      # Initialize a list to hold lists of step'd parameter values (independent)
    current_list = []    # Initialize a list to hold current .meas values
    all_lists_names = [] # Initialize a list to hold names of .meas lists
    all_lists = []       # Initialize a list to hold all .meas lists ( dependent, yay 5*5000 array)
    
    with open(fname, mode='r') as log_file: #generator function
        for line in log_file:
            
            log_parse_line(line)            #do all the work
        
        if current_list:all_lists.append(current_list)# append the last list to all_lists (if it's not empty)
    
    return all_lists, all_lists_names, step_lists, step_names

def log_parse_line(linestr):
    """ decide what to do with each line of the log file and append to lists for plotting """
    global current_list, all_lists, all_lists_names, step_lists, step_names
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
            current_list.append(np.float64(linestr.split('\t')[1].strip()))
        
        #step data
        elif linestr.startswith(".step"):
            if not step_names:
                step_names = linestr[6:].replace('=',' ').split(' ')[::2] #if it hasn't been done already copy step'd parameter names into storage
                for i in range(len(step_names)):step_lists.append([])     #and set the number of independent step'd parameters that will be stored
            
            for index, val in enumerate(linestr[6:].replace('=',' ').split(' ')[1::2]): step_lists[index].append(np.float64(val.strip())) #append step parameters into storage
        
        #new measurement/name
        elif linestr.startswith("Measurement:"):
            #print(linestr,'new measurement')
            all_lists_names.append(linestr.split(":")[1].strip()) #copy measurement name into storage
            
            if current_list:                    #if current list is NOT empty (skip first)
                all_lists.append(current_list)  #copy measurements into storage (makes a list of lists)
                current_list = []               #reset current_list for the new measurement

        return None
    
    except (ValueError,IndexError) as e: return None




if __name__ == "__main__":
    #to look for a log file
    from tkinter import filedialog

    def open_file_dialog():
        file_path = filedialog.askopenfilename(filetypes=[("Log files", "*.log")])
        if file_path:
            print("Selected file:", file_path)
        else:
            print("No file selected.")
        return file_path

    logfilepath = open_file_dialog()
        
    global all_lists, all_lists_names, step_lists, step_names
    log_parser(logfilepath)
    
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    
    # Initial data to plot
    current_index = 0
    x = np.array(step_lists[0])  # Convert to numpy array
    y = np.array(step_lists[1])  # Convert to numpy array
    z = np.array(all_lists[current_index])   # Convert to numpy array
    
    # matplotlib doesn't seem to display log scale correctly in 3d so I have to do it this way
    x_log = np.log10(x) 
    y_log = np.log10(y)
    
    # reshape coordinates for wireframe
    n = len(set(step_lists[0]))
    m = len(set(step_lists[1]))
    x_grid = np.array(x_log).reshape((m, n))
    y_grid = np.array(y_log).reshape((m, n))
    z_grid = np.array(z).reshape((m, n))
   
    # Create wireframe once
    global wireframe
    wireframe = ax.plot_wireframe(x_grid, y_grid, z_grid)


    # Function to update plot when switching between datasets
    def update_plot(index):
        global current_index
        current_index = index
        z = np.array(all_lists[current_index])
        z_grid = np.array(z).reshape((m, n))
        global wireframe
        wireframe.remove()  # Remove old wireframe
        wireframe = ax.plot_wireframe(x_grid, y_grid, z_grid)  # Create new wireframe
        ax.set_zlabel(all_lists_names[current_index])
        plt.draw()

    # Add a button to switch between datasets
    ax_button = plt.axes([0.8, 0.05, 0.1, 0.075])
    button = plt.Button(ax_button, 'Switch')

    def on_button_click(event):
        update_plot((current_index + 1) % len(all_lists_names))
    button.on_clicked(on_button_click)

    ax.set_xlabel('log(' + step_names[0] + ')')
    ax.set_ylabel('log(' + step_names[1] + ')')
    ax.set_zlabel(all_lists_names[current_index])
    ax.set_title('generic toad')

    plt.show()