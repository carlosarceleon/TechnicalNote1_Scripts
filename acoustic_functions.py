import os
import matplotlib.pyplot as plt
from math import log10
import pandas as pd
from numpy import array
import seaborn as sns
from matplotlib import rc
from matplotlib.ticker import ScalarFormatter


#rc('text',usetex=True)
#
#sns.set_context('paper')
#sns.set_style("whitegrid")
#sns.set(font='serif',font_scale=2.5,style='whitegrid')
#rc('font',family='serif', serif='cm10')
#
line_styles = ['--','-.',':']
markers = [
        u'o', u'v', u'^', u'<', u'>', u'8', u's', u'p', u'*', 
    u'h', u'H', u'D', u'd'
]
#
#colors = [
#        '#013F70',
#        '#70A288',
#        '#D5896F',
#        '#BB9F06',
#        '#DAB785',
#        ]

def to_db(spd):
    #return spd
    return 10.*array(map(log10,spd))

def narrow_to_third_octave(frequencies,measurements):
    """ Calculates the equivalent third octave band spectrum
    for the given narrow band one.

    Inputs:
        frequencies: the frequencies of the given measurement
        measurements: the levels for those frequencies
    Outputs:
        bands: the levels of the third octave bands
        one_third_freq_center: the center of the third octave bands


    """
    from numpy import zeros
    import pandas as pd

    one_third_freq_center = [16, 20, 25, 31.5, 40, 50, 63, 80, 
                             100, 125, 160, 200, 250, 315, 400, 
                             500, 630, 800, 1000, 1250, 1600, 
                             2000, 2500, 3150, 4000, 5000, 6300, 
                             8000, 10000, 12500, 16000, 20000];

    lower_bands = [14.1, 17.8, 22.4, 28.2, 35.5, 44.7, 56.2, 70.8, 
                   89.1, 112, 141, 178, 224, 282, 355, 447, 562, 
                   708, 891, 1122, 1413, 1778, 2239, 2818, 3548, 
                   4467, 5623, 7079, 8913, 11220, 14130, 17780]
    upper_bands = [17.8, 22.4, 28.2, 35.5, 44.7, 56.2, 70.8, 89.1, 
                   112, 141, 178, 224, 282, 355, 447, 562, 708, 891, 
                   1122, 1413, 1778, 2239, 2818, 3548, 4467, 5623, 
                   7079, 8913, 11220, 14130, 17780, 22390]


    df = pd.DataFrame(data={'spl':measurements,'f':frequencies})

    bands = zeros(len(upper_bands))

    # Compute the acoustic absorption coefficient per 1/3 octave band

    # Here goes the distribution of the existing narrow band
    # frequencies into their respective third octave bands
    for a in range(len(upper_bands)):

        # If all the narrow bands are lower than this third octave bin,
        # set it to zero
        if len(df[ (df['f']>=lower_bands[a]) & \
                  (df['f']<upper_bands[a]) ]['spl'].values) == 0:
            pass

        # If there is only one narrow band in this third octave
        # band, then skip the addition and just return its value
        elif len(df[ (df['f']>=lower_bands[a]) & \
                    (df['f']<upper_bands[a]) ]['spl'].values) == 1:
            bands[a] = df[ (df['f']>=lower_bands[a]) & \
                          (df['f']<upper_bands[a]) ]['spl'].values

        # Else, for all narrow bands found inside this particular
        # third octave band, do a logarithmic summation over
        # them
        else:
            for L in df[ (df['f']>=lower_bands[a]) & \
                        (df['f']<upper_bands[a]) ]['spl'].values:
                bands[a] += 10.**(L/10.)
            bands[a] = 10.*log10(bands[a])

    return bands,one_third_freq_center


def read_mat_file(mat_file):
    from scipy.io import loadmat
    return loadmat(mat_file)

def compare_cases(cases={},plot_name="comparison.png",
                  use_third_octave=True,relative_to=False,
                  campaign='MarchData'):
    import pandas as pd
    spectrum_file_name = 'psd_pointsource.mat'

    root_folder = os.path.join(
        "/media/carlos/6E34D2CD34D29783/2015-03_SerrationAcoustics/",
        campaign)

    palette = sns.color_palette("cubehelix", n_colors=len(cases)+1)

    spectra = []
    relative_to_spectra = []
    for case in cases.keys():
        spectra.append(read_mat_file(
            os.path.join(root_folder,
                         case,
                         "CBFMaps_2048",
                         "integration",
                         spectrum_file_name)
        ))
    if relative_to:
       for case in relative_to.keys():
           relative_to_spectra.append(
               read_mat_file(os.path.join(
                   root_folder,case,"CBFMaps_2048","integration",
                   spectrum_file_name))
           )

    spectra_df = []
    for s in spectra:
        spectra_df.append(
                pd.DataFrame(
                    data = {
                        "f" : s['f'][0],
                        'psd' : s['psd'][0]
                        }, 
                    index=range(len(s['f'][0]))
                )
                )
    if relative_to:
       relative_to_spectra_df = []
       for s in relative_to_spectra:
           relative_to_spectra_df.append(
                   pd.DataFrame(
                       data = {
                           "f" : s['f'][0],
                           'psd' : s['psd'][0]
                           }, 
                       index=range(len(s['f'][0]))
                   )
                   )


    fig = plt.figure()
    ax = plt.subplot(111)

    ste_color_pass = False
    for s,c,cnt in zip(spectra_df,cases.values(),
                       range(len(cases.values()))):
        if "Slitted" in c:
            ls = '--'
        else:
            ls = '-'
        spectrum_frequencies = s[s['psd']!=0]['f'].values
        spectrum_spd = s[s['psd']!=0]['psd'].values
        spectrum_spd_db = to_db(spectrum_spd)
        if use_third_octave:
            spectrum_spd_db,frequencies = narrow_to_third_octave(
                    spectrum_frequencies,
                    spectrum_spd_db
                    )
        else:
            frequencies = spectrum_frequencies
        ls = line_styles[cnt]
        if "STE" in cases.keys()[cnt] and not ste_color_pass:
            color = 'k';lw=4
            ste_color_pass = True
            ls = '-'
        else:
            color = colors[cnt]; lw=4
        plt.plot(
            frequencies,
            spectrum_spd_db,
            color=palette.as_hex()[cnt],
            label=c,
            lw=lw,
            ls=ls
        )
    if relative_to:
       for s,c,cnt in zip(relative_to_spectra_df,relative_to.values(),
                          range(len(relative_to.values()))):
           ls = '--'
           spectrum_frequencies = s[s['psd']!=0]['f'].values
           spectrum_spd = s[s['psd']!=0]['psd'].values
           spectrum_spd_db = to_db(spectrum_spd)
           if use_third_octave:
               spectrum_spd_db,frequencies = narrow_to_third_octave(
                       spectrum_frequencies,
                       spectrum_spd_db
                       )
           else:
               spectrum_spd_db = 10.*array(map(log10,spectrum_spd))
               frequencies = spectrum_frequencies
           plt.plot(frequencies,spectrum_spd_db,
                    color=palette.as_hex()[cnt],label=c,
                    lw=lw,ls=line_styles[cnt])

    freq_df = pd.DataFrame(dict( zip(frequencies,spectrum_spd_db) ),
                           index=['spd']).T
    min_freq = min(freq_df[freq_df['spd']!=0].index)
    max_freq = max(freq_df[freq_df['spd']!=0].index)

    ax.legend(loc="lower right",framealpha=0.5)
    ax.set_ylim(-90,-60)
    ax.set_xlabel('$f$ [Hz]')
    ax.set_ylabel("Sound pressure level [dB]")
    ax.set_xlim(min_freq,max_freq)
    ax.set_xscale('log')
    ax.set_xticks([1000,2000,3000,4000,5000])
    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    plt.setp( ax.xaxis.get_majorticklabels(), rotation=0 )
    plt.grid(True,which='both')
    plt.savefig(plot_name,bbox_inches='tight')

def interpolate_to_find_crossover(frequencies,spl):
    from scipy.interpolate import UnivariateSpline

    s = UnivariateSpline(frequencies,spl,s=0)
    root = []
    for r in s.roots():
        if r>=1000 and r<=5000:
            root.append(r)

    if len(root)==1: return root[0]
    else: return 0

def get_crossover(root_folder,case,relative_to,
                  campaign='MarchData'):
    import pandas as pd

    spectrum_file_name = 'psd_pointsource.mat'

    case_spectrum = read_mat_file(os.path.join(
        root_folder,case,"CBFMaps_2048","integration",
        spectrum_file_name))
    relative_to_spectrum = read_mat_file(os.path.join(
            root_folder,relative_to,"CBFMaps_2048","integration",
            spectrum_file_name))


    case_spectrum_df = pd.DataFrame(
        data = {
            "f" : case_spectrum['f'][0],
            'psd' :case_spectrum['psd'][0]
            }, 
        index=range(len(case_spectrum['f'][0]))
    )
    relative_to_spectrum_df = pd.DataFrame(
        data = {
            "f" : relative_to_spectrum['f'][0],
            'psd' :relative_to_spectrum['psd'][0]
            }, 
        index=range(len(relative_to_spectrum['f'][0]))
    )

    spectrum_frequencies = case_spectrum_df[
        case_spectrum_df['psd']!=0]['f'].values
    base_spectrum_frequencies = relative_to_spectrum_df[
        relative_to_spectrum_df['psd']!=0]['f'].values
    spectrum_spd = case_spectrum_df[
        case_spectrum_df['psd']!=0]['psd'].values
    base_spectrum_spd = relative_to_spectrum_df[
        relative_to_spectrum_df['psd']!=0]['psd'].values
    
    spectrum_third_octv,frequencies = narrow_to_third_octave(
            spectrum_frequencies,
            10.*array(map(log10,spectrum_spd))
            )
    base_spectrum_third_octv,frequencies_base = \
            narrow_to_third_octave(
            base_spectrum_frequencies,
            10*array(map(log10,base_spectrum_spd))
            )

    crossover = interpolate_to_find_crossover(
        frequencies,base_spectrum_third_octv-spectrum_third_octv
    )
    return crossover

def compare_cases_relative(cases={},relative_to={},
                           plot_name="comparison_relative.png",
                           title=True,campaign='MarchData'):
    from numpy import array

    spectrum_file_name = 'psd_pointsource.mat'

    root_folder = os.path.join(
        "/media/carlos/6E34D2CD34D29783/2015-03_SerrationAcoustics/",
        campaign)
    palette = sns.color_palette("cubehelix", n_colors=len(cases)+1)

    spectra = []
    relative_to_spectra = []
    for case in cases.keys():
        spectra.append(read_mat_file(os.path.join(
            root_folder,case,"CBFMaps_2048","integration",
            spectrum_file_name)))

    for rel_to in relative_to.keys():
        relative_to_spectra.append(
            read_mat_file(os.path.join(
                root_folder,rel_to,"CBFMaps_2048","integration",
                spectrum_file_name))
        )

    spectra_df = []
    for s in spectra:
        spectra_df.append(
                pd.DataFrame(
                    data = {
                        "f" : s['f'][0],
                        'psd' : s['psd'][0]
                        }, 
                    index=range(len(s['f'][0]))
                )
                )
    spectra_df_relative_to = []
    for r in relative_to_spectra:
        spectra_df_relative_to.append(
            pd.DataFrame(
                    data = {
                        "f" : r['f'][0],
                        'psd' : r['psd'][0]
                        }, 
                    index=range(len(r['f'][0]))
                )
            )

    fig = plt.figure()
    ax = plt.subplot(111)

    crossover_file = open(os.path.splitext(plot_name)[0]+".csv",'w')
    for s,c,cnt in zip(spectra_df,cases.values(),
                       range(len(cases.values()))):
        if len(relative_to.values())==1:
            r = spectra_df_relative_to[0]
            rc = relative_to.values()[0]
        else:
            r = spectra_df_relative_to[cnt]
            rc = relative_to.values()[cnt]

        if "Slitted" in c:
            ls = '--'
        else:
            ls = '-'
        spectrum_frequencies      = s[s['psd']!=0]['f'].values
        base_spectrum_frequencies = r[r['psd']!=0]['f'].values
        spectrum_spd              = s[s['psd']!=0]['psd'].values
        base_spectrum_spd         = r[r['psd']!=0]['psd'].values

        spectrum_third_octv,frequencies = narrow_to_third_octave(
                spectrum_frequencies,
                10.*array(map(log10,spectrum_spd))
                )
        base_spectrum_third_octv,frequencies_base = \
                narrow_to_third_octave(
                base_spectrum_frequencies,
                10*array(map(log10,base_spectrum_spd))
                )

        ax.plot(
                frequencies,
                base_spectrum_third_octv-spectrum_third_octv,
                line_styles[cnt],
                color=palette.as_hex()[cnt],
                label=c,
                lw=4
                )
        crossover = interpolate_to_find_crossover(
            frequencies,base_spectrum_third_octv-spectrum_third_octv
        )
        crossover_file.write(
            "{0},{1:.0f}\n".format(c,crossover)
        )
    crossover_file.close()

    freq_df = pd.DataFrame(
        dict( zip(frequencies,spectrum_third_octv) ),index=['spd']
    ).T
    min_freq = min(freq_df[freq_df['spd']!=0].index)
    max_freq = max(freq_df[freq_df['spd']!=0].index)

    #if title:
    #    plt.title(title)
    ax.legend(loc="lower left",framealpha=0.5)
    #plt.semilogx()
    ax.set_xlabel('$f$ [Hz]')
    ax.set_ylabel("Reduction [dB]")
    ax.set_xlim(min_freq,max_freq)
    ax.set_ylim(-10,10)
    ax.set_xscale('log')
    ax.set_xticks([1000,2000,3000,4000,5000])
    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    plt.setp( ax.xaxis.get_majorticklabels(), rotation=0 )
    #ax.set_grid(True,which='both',ls="-", color='0.65')
    plt.savefig(plot_name,bbox_inches='tight')
    #plt.clear()

def process_integration(cases = []):

    def write_configuration_file(root_dir = False, 
                                 data_dir = False, cal_dir = False, 
                                 overwrite = True,nproc=4, 
                                 intregion = (-0.1,0.1,0.05,0.15),
                                 dynintregion=(-0.5,0.5,-1.0,1.0),
                                 filename = "integration.cfg"
                                ):
        import configparser
        from os.path import join,realpath,isfile
        if not all((root_dir, data_dir)):
            print(
                "ERROR: you missed to write in at least one parameter"
            )
            return 0
        root_dir = realpath(root_dir)
        if not overwrite and isfile(join(root_dir,data_dir,filename)):
            return 2

        config = configparser.ConfigParser()
        config['Acquisition'] = {
                "array"     : "Array_Delft_64_v3_int",
                "zs"        : "1.03",
                "fs"        : "50000",
                "c0"        : "343",
                "uc"        : "0,30,0",
                "zsl"       : "0.85",
                "exportraw" : "True",
                "exportwav" : "False",
                }
        config['Calibration'] = {
                'calibration' : 'True',
                'caloption'   : 'high',
                'caldir'      : cal_dir+"/",
                }
        config['Directories'] = {
                'rootdir' : root_dir+"/",
                'datadir' : data_dir+"/",
                }
        config['Beamforming'] = {
                "beamform"    : "True",
                "specify_f"   : "True",
                "f"           : "1000,5000,1",
                "nfft"        : "2048",
                "overlap"     : "0.75",
                "maxbln"      : "3000000",
                "bfrange"     : "1,2",
                "exportmap"   : "False",
                #"ignoremic"   : "7,15,23,31,39,47,55,63",
                "ignoremic"   : "26",
                "compute_csm" : "True",
                }
        config['Grid'] = {
                "xs"                : "-0.5,0.5,100",
                "ys"                : "-0.3,0.3,100",
                "dynamicresolution" : "True",
                "dynresmax"         : "-5.,5.,-5.,5.",
                "dynresres"         : "0.1,0.1",
                }
        config['CLEAN'] = {
                "deconv"    : "False",
                "phi"       : "0.15",
                "aratio"    : "0.02",
                "dmethod"   : "clean-sc",
                "cleanbeam" : "psf",
                }
        config["Integration"] = {
                "integrate"    : "True",
                "intfrom"      : "CBF",
                "intregion"    : "{0},{1},{2},{3}".format(
                    intregion[0],intregion[1],intregion[2],
                    intregion[3]
                ),
                "dynint"       : "False,True",
                "dynintregion" : "{0},{1},{2},{3}".format(
                    dynintregion[0],dynintregion[1],dynintregion[2],
                    dynintregion[3]
                ),
                "sourcetype"   : "pointsource",
                "exportIntMap" : "True",
                }
        config["DAMAS"] = {
                "ndamas" : "1",
                }
        config["Others"] = {
                "compute_snr" : "False",
                "resolution"  : "False",
                "psf"         : "False",
                "psd"         : "False",
                "csm"         : "False",
                "diagelim"    : "True",
                "density"     : "False",
                "dynaperture" : "False",
                "showarray"   : "False",
                "proc"        : str(nproc),
                }


        with open(join(root_dir,data_dir,'config.cfg'), 'w') \
                as configfile:
            config.write(configfile)
        return 1

    def write_all_configuration_files(root_dir,case_folders,\
                                      overwrite=True,nproc=1,\
                                      cal_dir=False):
        for f in case_folders:
            write_configuration_file(root_dir,f,overwrite=overwrite,\
                                     nproc=nproc,cal_dir=cal_dir)

    def execute_parallel_analysis(root_dir,case_folders,nproc = 4, \
                                  clear_existing=False):

        from subprocess import Popen
        from os.path import join,realpath
        import time,sys

        analysis_script = realpath("./pyarray_v4a.pyc")
        cal_dir = realpath("./")

        #if clear_existing:
        #    clear_existing_analysis(root_dir,case_folders)

        write_all_configuration_files(root_dir,case_folders,\
                                      nproc=nproc,cal_dir=cal_dir)

        command = ['python',analysis_script,'config.cfg']
        root_dir = realpath(root_dir)

        def exec_runs(case_folders):
            def done(p):
                return p.poll() is not None
            def success(p):
                return p.returncode == 0
            def fail():
                sys.exit(1)

            max_cases = 2 # Number of cases to run at the same time
            processes = []
            while True:
                while case_folders and len(processes) < max_cases:
                    case = case_folders.pop()
                    #print list2cmdline(case)
                    processes.append(
                        Popen(command,cwd=join(root_dir,case))
                    )

                for p in processes:
                    if done(p):
                        if success(p):
                            processes.remove(p)
                        else:
                            fail()

                if not processes and not case_folders:
                    break
                else:
                    time.sleep(0.05)

        exec_runs(case_folders)

    if len(cases)==0:
        cases = [
                "2015-03-05_18-51-42_Sr20R21_a12_p0_U35_repitability/" ,
                "2015-03-05_14-37-04_Sr20R21_a12_p0_U30"               ,
                "2015-03-05_14-38-59_Sr20R21_a12_p0_U35"               ,
                "2015-03-05_14-40-51_Sr20R21_a12_p0_U40"               ,
                "2015-03-05_18-49-47_Sr20R21_a12_p0_U30_repitability"  ,
                "2015-03-05_18-53-21_Sr20R21_a12_p0_U40_repitability"  ,
                ]

    execute_parallel_analysis(
            "/media/carlos/6E34D2CD34D29783/2015-03_SerrationAcoustics/",
            cases,
            nproc = 4,
            clear_existing = False
            )

def run_all_folders():
    def get_all_cases(root_dir = '.'):
        from os import listdir
        from os.path import isfile,join
        avaiable_folders = [f for f in listdir(root_dir)]
        case_folders = []
        for f in avaiable_folders:
            if isfile(join(root_dir,f,"acoustic_data")):
                case_folders.append(f)
        return case_folders
    process_integration(cases=get_all_cases("../"))


def run_missing_folders():
    def get_all_cases(root_dir = '.'):
        from os import listdir
        from os.path import isfile,join
        avaiable_folders = [f for f in listdir(root_dir)]
        case_folders = []
        for f in avaiable_folders:
            if isfile(join(root_dir,f,"acoustic_data")):
                case_folders.append(f)
        return case_folders
    def get_missing_cases(root_dir,case_folders):
        from os.path import isfile,join
        missing_folders = []
        for f in case_folders:
            if not isfile(join(
                root_dir,f,"CBFMaps_2048","integration",
                "psd_pointsource.mat"
            )):
                missing_folders.append(f)
        return missing_folders
    process_integration(cases=get_missing_cases(
        "../",get_all_cases("../")
    ))

def move_data_to_local(origin,target):
    from shutil import copy
    from os.path import join

    acoustic_data_subdirs = join(
        'CBFMaps_2048','integration','psd_pointsource.mat'
    )

    copy(join(origin,acoustic_data_subdirs),target)



####################################################################
##           Solid, different alpha U35, phi 6
####################################################################
#cases = OrderedDict([
#        ("Sr05R31_a12_p0_U35",      "Sr05R31 (S1)"),
#        ("Sr10R31_a12_p0_U35",      "Sr10R31 (S2)"),
#        ("Sr05R21_a12_p0_U35",      "Sr05R21 (S3)"),
#        ("Sr10R21_a12_p0_U35",      "Sr10R21 "),
#        ])
#relative_to = OrderedDict([
#        ("STE_a12_U35", "straight trailing edge, $\\alpha_g = 12^\circ$"),
#        ("STE_a12_U35", "straight trailing edge, $\\alpha_g = 12^\circ$"),
#        ("STE_a12_U35", "straight trailing edge, $\\alpha_g = 12^\circ$"),
#        ("STE_a12_U35", "straight trailing edge, $\\alpha_g = 12^\circ$"),
#        ])
#title = ""
#compare_cases_relative(cases=cases,relative_to=relative_to,plot_name="images/Relative_Small_serrations_a12_p0.png",title=title)
#compare_cases(cases=cases,plot_name="images/Small_serrations_a12_p0.png", relative_to=relative_to,use_third_octave=False)
