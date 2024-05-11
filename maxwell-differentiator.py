#   sean heffley electrodynamics 2
## import 
try:
    import scipy as sp
    import numpy as np
    import matplotlib.pyplot as plt
except:
    raise ImportError('scipy, numpy, or matplotlib did not import')

## define constants
E_max       = np.float64(100)            #V/m at t=0
beta        = np.float64(0.1)            #velocity factor
sigma       = np.float64(5   *10**(-9 )) #kg^-1m^-2s^3A^2
c           = np.float64(3   *10**( 8 )) #ms^-2
epsilon_0   = np.float64(8.55*10**(-12)) #N^-1m^-2C^2
k           = np.float64(1.18*10**( 7 )) #from problem 1

#vector system
#[dw0dx] == [w1]
#[dw1dx] == [w2] == -(2m/(hbar^2))*(e-u)*[w0] == -g[w0]

#vector system 1st order
def vector_ode_Ez(E, z):
    de0dz = E[1]
    de1dz = (sigma)/(beta*c*epsilon_0)*E[1] + (k**2)*E[0]
    return [de0dz, de1dz]

def vector_ode_Et(E, t):
    de0dt = E[1]
    de1dt = (c**2 * k**2)*E[0]
    return [de0dt, de1dt]


def vectorSystemODE(function, W0, independent):
    """returns a python list containg function(array value), 
        basically just to document/comment
    
        independent: iterable values
        W0 : initial values of the vector system
    """
    W = sp.integrate.odeint(function, W0, independent) 
    return list(W[:,0]) #python list of the first column (i.e. de0dz)

if __name__ == "__main__":
    z_linspace = np.linspace(90, 100, 100)
    Ez0 = [100, 100]

    t_linspace = np.linspace(90, 100, 100)
    Et0 = [100, 100]

    Ez = vectorSystemODE(vector_ode_Ez, Ez0, z_linspace)
    Et = vectorSystemODE(vector_ode_Et, Et0, t_linspace)

    ## borrowing some code from my ltspice plotter
    """ how these are originally defined
    step_lists_names = []   # Initialize a list to hold step'd parameter names
    step_lists = []         # Initialize a list to hold lists of step'd parameter values (independent)
    current_meas_list = []  # Initialize a list to hold current .meas values
    meas_lists_names = []   # Initialize a list to hold names of .meas lists
    meas_lists = []         # Initialize a list to hold all .meas lists ( dependent, yay 5*5000 array)
    """
    #making data the same format
    stepz = [z_linspace]*len(t_linspace)
    stept = [t_linspace]*len(z_linspace)
    stept.sort()

    measEz = Ez*len(t_linspace)
    measEt = Et*len(z_linspace)
    measEt.sort()

    measEzt = np.outer(Ez, Et).flatten()

    meas_lists          = [[measEz],[measEt],[measEzt]]
    meas_lists_names    = ['Et','Ez','Ezt']
    step_lists          = [stepz,stept]
    step_lists_names    = ['z','t']


    
    x = np.array(step_lists[0])# Convert data to numpy array
    y = np.array(step_lists[1])# Convert data to numpy array
    z = np.array(meas_lists[0])# Convert data to numpy array, init with index 0
    xy_shape = (len(set(y)), len(set(x))) #number of unique elements in x and y axis


    from matplotlib.ticker import AutoLocator

    #///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    #setup some plot stuff
    fig = plt.figure(figsize=(16, 12), dpi=80)
    ax = plt.axes(projection='3d')
    ax.set_proj_type('ortho')  #persp, ortho
    plt.subplots_adjust(bottom=0)
    ax.set_title(logfilename)

    #linear or log, matplotlib axis scale workaround (and it's been a known issue in 3d for 13+years)
    xscale = 'linear'
    yscale = 'linear'
    zscale = 'linear'

    #when to use scientific vs positional representation for readability
    def log_use_scientific(number):   return (number <= -4 or number >= 6)
    def lin_use_scientific(number):   return (number <= -(10**6) or number >= (10**6))

    #scientific representations
    def log_format_scientific(number):
        return np.format_float_scientific(10**number,precision=1,unique=True,trim='-',sign=False)
    def lin_format_scientific(number):
        return np.format_float_scientific(    number,precision=1,unique=True,trim='-',sign=False)

    #positional representations 
    def log_format_positional(number):
        number = np.float64(np.format_float_scientific(10**number,precision=2))     #the built in precision only handles decimal points
        return np.format_float_positional(number,unique=True,trim='-',sign=False)   #here's a worksround for 3sigfig
    def lin_format_positional(number):
        number = np.float64(np.format_float_scientific(    number,precision=2))
        return np.format_float_positional(number,unique=True,trim='-',sign=False)

    #///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    #functions that handle data
    def setup_grid(dataset,scale):
        if scale == 'log':return np.log10(dataset).reshape(xy_shape)
        elif scale == 'linear':return dataset.reshape(xy_shape)
        else: raise ValueError(f'invalid scale {scale}')

    def setup_ticks(axis): #TODO limit sig figures in tick_locs before re-assigning instead of in format ticks
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
        
    #///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    #actually doing stuff with data finally

    wireframe = ax.plot_wireframe(setup_grid(x,xscale), setup_grid(y,yscale), setup_grid(z,zscale))

    ax.set_xlabel(step_lists_names[0])
    ax.set_ylabel(step_lists_names[1])
    ax.set_zlabel(meas_lists_names[0])
    setup_ticks('x')
    setup_ticks('y')
    setup_ticks('z')

    wireframe.remove()  # Reset wireframe, for some reason it plots smaller the first time ¯\_(ツ)_/¯
    wireframe = ax.plot_wireframe(setup_grid(x,xscale), setup_grid(y,yscale), setup_grid(z,zscale) ,label=meas_lists_names[0])
    #///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    #buttons to do stuff with the functions that handle data

    # Function to update which meas data is shown
    def switch_meas_plot(new_index):
        global z, wireframe
        z = np.array(meas_lists[new_index])

        wireframe.remove()  # Remove old wireframe
        wireframe = ax.plot_wireframe(setup_grid(x,xscale), setup_grid(y,yscale), setup_grid(z,zscale), label=meas_lists_names[new_index]) # Create new wireframe

        ax.set_zlabel(meas_lists_names[new_index])

        #ax.zaxis.set_major_locator(AutoLocator())
        setup_ticks('z')

        plt.draw()
        ax.legend()

    # Add buttons to cycle between datasets
    global current_index
    current_index = 0

    def on_cycle_next(event):
        global current_index
        current_index = (current_index + 1) % len(meas_lists_names)
        switch_meas_plot(current_index)
    button_next = plt.Button(plt.axes([0.8, 0.075, 0.1, 0.075]), 'Next')
    button_next.on_clicked(on_cycle_next)

    def on_cycle_prev(event):
        global current_index
        current_index = (current_index - 1) % len(meas_lists_names)
        switch_meas_plot(current_index)
    button_prev = plt.Button(plt.axes([0.9, 0.075, 0.1, 0.075]), 'Prev')
    button_prev.on_clicked(on_cycle_prev)

    #add buttons to keep a copy of the current wireframe, or clear the copies
    global temp_wireframes
    temp_wireframes = []

    def on_keep_wireframe(event):
        global z, temp_wireframes
        print(current_index)
        temp_wireframes.append(ax.plot_wireframe(setup_grid(x,xscale), setup_grid(y,yscale), setup_grid(z,zscale),\
            color = np.random.rand(3,), label=meas_lists_names[current_index]))
        plt.draw()
        ax.legend()
    button_keep = plt.Button(plt.axes([0.8, 0.00, 0.1, 0.075]), 'Keep')
    button_keep.on_clicked(on_keep_wireframe)

    def on_clear_wireframes(event):
        global temp_wireframes
        for frame in temp_wireframes:
            frame.remove()  # Remove old wireframe from plot
        temp_wireframes = [] #Remove pointers to nothing
        plt.draw()
        ax.legend()
    button_clear = plt.Button(plt.axes([0.9, 0.00, 0.1, 0.075]), 'Clear')
    button_clear.on_clicked(on_clear_wireframes)

    plt.show()