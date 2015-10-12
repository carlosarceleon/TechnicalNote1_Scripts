import os
import pandas as pd
import TELocations as teloc
import numpy as np
import re

file_dict = {
    'Avg_Vx'                            : "B00001.dat",
    'Avg_Vy'                            : "B00002.dat",
    'Length_of_Avg_V'                   : "B00003.dat",
    'Standard_deviation_of_Vx'          : "B00004.dat",
    'Standard_deviation_of_Vy'          : "B00005.dat",
    'Length_of_Standard_deviation_of_V' : "B00006.dat",
    'Turbulent_kinetec_energy'          : "B00007.dat",
    'Reynold_stress_XY'                 : "B00008.dat",
    'Reynold_stress_XX'                 : "B00009.dat",
    'Reynold_stress_YY'                 : "B00010.dat",
}

davis_dict = {
    'Avg_Vx'                            : 'Avg_Vx'                   ,
    'Avg_Vy'                            : 'Avg_Vy'                   ,
    'Length_of_Avg_V'                   : 'Length_of_Avg_V'          ,
    'Standard_deviation_of_Vx'          : 'RMS_Vx'                   ,
    'Standard_deviation_of_Vy'          : 'RMS_Vy'                   ,
    'Length_of_Standard_deviation_of_V' : 'Length_of_RMS_V'          ,
    'Turbulent_kinetec_energy'          : 'Turbulent_kinetec_energy' ,
    'Reynold_stress_XY'                 : 'Reynold_stress_XY'        ,
    'Reynold_stress_XX'                 : 'Reynold_stress_XX'        ,
    'Reynold_stress_YY'                 : 'Reynold_stress_YY'        ,
}

root = '/media/carlos/6E34D2CD34D29783/2015-07_BL/STE_BL_Data/'

data_folders = [f for f in os.listdir(root) \
                if os.path.isdir(os.path.join(root,f))]

def read_data(root,case,variable):
    """ Reads the data. Prioritize reading an existing pickle
    of the data"""
    import os
    import pandas as pd

    if os.path.isfile(
        os.path.join(root,case+'.p')
    ):
        return pd.read_pickle(
            os.path.join(root,case+".p")
        )
    else:
        tecplot_file = os.path.join(root,case,file_dict[variable])
        return read_tecplot(tecplot_file)



def read_tecplot(tecplot_file):
    """Reads in (the second frame present in the given) tecplot file, 
    and returns a pandas data frame

    Input:
        tecplot formated file
    Output:
        pandas data frame

    """

    # Get available variables
    f = open(tecplot_file,'ro')

    variables = []
    # Do two things:
        # 1) Grab the important info from the header
        # 2) See where the second frame info starts so that 
        #       it passes it later to the pandas reader
    var_string = 0
    end_line   = 0
    final_line = 0
    stop_frame_count = False
    for line in f:
        if not stop_frame_count:
            end_line+=1
        if 'Frame 2' in line:
            stop_frame_count = True
        if not var_string:
            var_string = re.findall("^VARIABLES[ _A-Za-z0-9,\"=]+",line)
        if var_string:
            variables = [
                v.replace(' ','_').replace("\"","") \
                for v in var_string[0].replace("VARIABLES = ",'').\
                split(", ")
            ]
            variables = [v for v in variables if len(v)]
        final_line += 1
    f.close()

    lines_to_skip = range(0,3)+range(end_line-1,final_line)

    # Put the data into a data frame
    data = pd.read_table(
            tecplot_file,
            skiprows  = lines_to_skip,
            names     = variables,
            sep       = '[ \t]+',
            index_col = False,
            dtype     = np.float
    )

    #data.x         = np.array(map(float,data.x))
    #data.y         = np.array(map(float,data.y))
    #data[variable] = np.array(map(float,data[variable]))


    data = data[
        (data.x < data.x.max()*0.90) &\
        (data.x > data.x.min()*1.10) &\
        (data.y < data.y.max()*0.90) &\
        (data.y > data.y.min()*1.10) 
    ]

    #if not variable in data.columns:
    #    print("Error: {0} not in file\nAvailable variable: {1}".\
    #         format(variable,data.columns[2]))
    #    return None
    #else:
    return data

def pickle_all_data(root,case_name):
    """ Meant to be used only once... pickles the (relevant) 
        TECPLOT data into a single file

    Input:
        TECPLOT file folder
    """

    variables_to_read = [
        'Avg_Vx'                  ,
        'Avg_Vy'                  ,
        'Length_of_Avg_V'
    ]

    for v in variables_to_read:
        if v == variables_to_read[0]:
            tecplot_file = os.path.join(root,case_name,file_dict[v])
            df = read_tecplot(tecplot_file)
        else:
            tecplot_file = os.path.join(root,case_name,file_dict[v])
            df_tmp = read_tecplot(tecplot_file)
            df[v] = df_tmp[v]

    df.to_pickle(os.path.join(root,case_name+'.p'))

def find_nearest(to_point,from_array):
   """ Finds the nearest available value in a array to a given value

   Inputs:
      to_point: value to find the nearest to in the array
      from_array: array of available values 
   Returns:
      The nearest value found in the array
   """
   deltas = np.ones(len(from_array))*1000
   for v,i in zip(from_array,range(len(from_array))):
       deltas[i] = abs(float(to_point) - float(v))

   return from_array[np.argmin(deltas)]

def recognize_case(case_name):
    """ Separates the case name folder into its distinctive parameters
    used in this campaign

    Input: folder name
    Output: 
        the key of the TELocations dictionary it belongs to
        case parameters [alpha,side,test_section]
    """

    alpha = int(re.findall('[Aa][0-9][0-9]?',case_name)[0]\
            .replace('A','').replace('a',''))
    try:
        side = re.findall('PS',case_name)[0]
    except:
        side = 'SS'
    try:
        test_section = re.findall('closed',case_name)[0]
    except:
        test_section = 'open'

    # A complicated search for equal terms in the dictionary keys and
    # the case parameters
    # (that's what happens when you don't use standard nomenclature)
    case_key = ''
    for keys,values in zip(
        teloc.TELocations.keys(),
        teloc.TELocations.values()
    ):
        if test_section == values[0]:
            if alpha == int(re.findall('[Aa][0-9][0-9]?',keys)[0]\
               .replace('A','').replace('a','')):
                if alpha: # Hey, alpha = 0 has no side
                    if side == re.findall('[PS]S',keys)[0]:
                        case_key = keys
                        break
                elif alpha==0:
                    case_key = keys
                    break

    case_parameters = [alpha,side,test_section]
    return case_key, case_parameters

def get_bl(case,variable='Avg_Vy'):
    """ Get the TE boundary layer information and return it as an array

    Input:
        tecplot file location
    Output:
        array of flow velocity values
        locations of those velocity vectors
    """

    df = read_data(root,case,variable)
    te_location = teloc.TELocations[
        recognize_case(case)[0]
    ][1]

    x = find_nearest(float(te_location[0]),df.x.unique())
    y = find_nearest(float(te_location[1]),df.y.unique())

    data = df[
        (df.y == y) &\
        (df.x < x)
    ]

    bl_data =   np.array(map(float,data[variable].values))
    points  = -(np.array(map(float,data['x'].values))-te_location[0])

    return bl_data,points

def plot_bl(case,variable='Avg_Vy'):
    from matplotlib import pyplot as plt
    import seaborn as sns
    sns.__version__

    x,y = get_bl(case,variable)

    fig = plt.figure()
    ax = plt.subplot(111)
    ax.plot(x,y,'-')
    loc_99,vel_99 = find_bl(case,variable)
    ax.scatter(vel_99,loc_99,marker='o',color='r',s=100)
    ax.text(vel_99-2,loc_99,'$\\delta_{{99}} ={0:.2f} $ mm'.\
            format(loc_99),ha='right',va='center')
    ax.set_xlabel('$v$ [m/s]')
    ax.set_ylabel('$y$ [mm]')
    ax.set_ylim(bottom=0)
    plt.title(case)
    plt.savefig('images/BL_{0}.png'.format(case))
    fig.clear()
    

def plot_surface(case,variable='Avg_Vy'):
    from matplotlib import pyplot as plt
    import seaborn as sns

    sns.set(context="notebook", style="whitegrid",
        rc={"axes.axisbelow": False,'image.cmap': 'YlOrRd'})

    df = read_data(root,case,variable)
    X,Y = np.meshgrid(df.x.unique(),df.y.unique())
    Z = df[variable].reshape(X.shape)
    te_location = teloc.TELocations[
        recognize_case(case)[0]
    ][1]

    bl_data,points  = get_bl(case=case,variable=variable)
    delta_99,vel_99 = find_bl(case=case,variable=variable)
    points   = -points+te_location[0]
    delta_99 = -delta_99+te_location[0]

    levels = np.linspace(float(Z.min()),float(Z.max())+1,30)
    fig = plt.figure()
    ax = plt.subplot(111,aspect=1)
    ax.contourf(X,Y,Z,levels=levels)
    C = ax.contour(X, Y, Z, levels=levels,
                       colors = ('k',),
                       linewidths = (1,),
              )
    ax.clabel(C, inline=1, fontsize=10,color='w')
    ax.scatter(points,[te_location[1]]*len(points),s=10,color='k')
    ax.scatter(delta_99,te_location[1],s=40,color='k')
    ax.scatter(delta_99,te_location[1],marker='x',s=80,color='k')
    plt.savefig('images/Surface_{0}.png'.format(case))
    fig.clear()

def find_bl(case,variable='Avg_Vy'):

    vel,loc = get_bl(case,variable)

    vel_99 = vel.max()*0.99
    for v,l in zip(vel[::-1],loc[::-1]):
        if v>vel_99:
            delta_99 = l
            break

    return delta_99,vel_99

#df = read_tecplot(os.path.join(root,data_folders[0],'B00001.dat'))
#variable = 'Length_of_Standard_deviation_of_V'#'Avg_Vy'
variable = 'Length_of_Avg_V'
for case in data_folders:
    #plot_bl(case,variable)
    plot_surface(case,variable)
    #pickle_all_data(root,case)

