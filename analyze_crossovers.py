import acoustic_functions as acfunc
import bl_functions as blfunc
import os

acoustic_root = \
        './AcousticData/'
acoustic_campaign = 'MarchData'

acoustic_data_path = os.path.join(acoustic_root)

devices = ['Sr20R21']
speeds = [30,35,40]
alphas = [0,6,12]
phis   = [0,6]

def get_case_name(device,speed,alpha,phi,campaign):
    """ Given a case information, build the case name as it was
    given for the dataset (the folder that contains the case)

    Input:
        device,speed,alpha,phi,campaign
    Output:
        string
    """

    if "March" in campaign:
        return "psd_{0}_a{1:02d}_p{2}_U{3}.mat".\
                format(
                    device,
                    alpha,
                    phi,
                    speed
                )
    if "July" in campaign:
        return "psd_{0}_a{1}_U{2}.mat".\
                format(
                    device,
                    alpha,
                    speed
                )


def get_crossovers():
    """ Gets the crossover of the given case permutations and
    returns a pandas Data Frame with all the information

    Output:
        pandas Data Frame
    """
    import pandas as pd

    crossover_df = pd.DataFrame(
        columns = [
            'campaign',
            'device',
            'alpha',
            'phi',
            'U',
            'crossover'
        ]
    )

    campaign = acoustic_campaign
    for dev in devices:
        for speed in speeds:
            for alpha in alphas:
                for phi in phis:
                    case_name = get_case_name(
                        dev,speed,alpha,phi,campaign
                    )
                    ste_case_name = case_name\
                            .replace(dev,"STE")\
                            .replace("_p{0}".format(phi),'')

                    crossover = acfunc.get_crossover(
                        root_folder=os.path.join(
                            acoustic_root),
                        case=case_name,
                        relative_to=ste_case_name,
                        #campaign='MarchData'
                    )

                    crossover_dict = {
                        'campaign'  : campaign,
                        'device'    : dev,
                        'alpha'     : alpha,
                        'phi'       : phi,
                        'U'         : speed,
                        'crossover' : crossover
                    }
                    crossover_df = crossover_df\
                            .append(crossover_dict,ignore_index=1)
    return crossover_df

def get_boundary_layers():
    return blfunc.make_csv(out_file=False)

def Strouhal(f,delta,U):
    Strouhal = f*delta/float(U)/1000.
    return Strouhal

def plot_bl_crossover_relation(article=False,real_Uinf=True):
    import matplotlib.pyplot as plt 
    from numpy import array,argmin
    import seaborn as sns
    from matplotlib import rc

    if article:
        rc('text',usetex=True)

        sns.set_context('paper')
        sns.set_style("whitegrid")
        sns.set(font='serif',font_scale=1.8,style='whitegrid')
        rc('font',family='serif', serif='cm10')

    crossover_df = get_crossovers()
    bl_df        = get_boundary_layers()
    #flatui = ["#3498db", "#95a5a6", "#e74c3c"]

    colormap = sns.color_palette(
        #flatui,
        'cubehelix',
        len(bl_df.U.unique())+1
    )
    markers = ['s','D','<','s']

    if article:
        fig,ax = plt.subplots(2,1,sharex=True,sharey=True)
    else:
        fig,ax = plt.subplots(3,1,sharex=True,sharey=True)
    crossover_df = crossover_df[crossover_df.crossover!=0]
    crossover_df = crossover_df[crossover_df.phi==6]

    done_labels = []
    for ix,acoustic_case in crossover_df.iterrows():

        delta = bl_df[
            (bl_df.U == acoustic_case.U) & \
            (bl_df.alpha == acoustic_case.alpha) & \
            (bl_df.Test_section == 'open')
        ]

        delta_ps   = delta[delta.Side=='PS'].Delta_BL
        delta_ss   = delta[delta.Side=='SS'].Delta_BL
        delta_zero = delta[delta.Side=='NA'].Delta_BL


        if delta_ps.shape[0]:
            Uinf_BL_ps = delta[delta.Side=='PS'].U_max.values[0]
            Uinf_BL_ss = delta[delta.Side=='SS'].U_max.values[0]
            delta_sum  = delta_ps.values[0]+delta_ss.values[0]
        else: 
            delta_sum = array([])
            Uinf_BL_zero = delta[delta.Side=='NA'].U_max.values[0]

        color = colormap[
            argmin(map(abs,delta.U.values[0]-bl_df.U.unique()))
        ]
        marker = markers[
            argmin(map(abs,delta.U.values[0]-bl_df.U.unique()))
        ]
        marker_size = 150
        alpha = 1.0

        if delta.U.values[0] in done_labels:
            label = ''
        else:
            label = "$U_\\infty = {{{0}}}$ m/s".format(
                acoustic_case.U
            )
            done_labels.append(delta.U.values[0])


        plot_args = {
            'edgecolors' : color,
            'alpha'      : alpha,
            's'          : marker_size,
            'label'      : label,
            'facecolors' : 'none',
            'linewidth'  : 3,
            'marker'     : marker,
        }

        # Presure side delta plot
        if delta_ps.shape[0]:
            if not real_Uinf:
                U_infty = acoustic_case.U
            else:
                U_infty = Uinf_BL_ps
            ax[0].scatter(
                acoustic_case.alpha,
                Strouhal(
                    acoustic_case.crossover,
                    delta_ps.values[0],
                    U_infty
                ),
                **plot_args
            )
        if delta_ss.shape[0]:
            if not real_Uinf:
                U_infty = acoustic_case.U
            else:
                U_infty = Uinf_BL_ss
            ax[1].scatter(
                acoustic_case.alpha,
                Strouhal(
                    acoustic_case.crossover,
                    delta_ss.values[0],
                    U_infty
                ),
                **plot_args
            )

            if not article:
                ax[2].scatter(
                    acoustic_case.alpha,
                    Strouhal(
                        acoustic_case.crossover,
                        delta_sum,
                        U_infty
                    ),
                    **plot_args
                )

        if delta_zero.shape[0]:
            if not real_Uinf:
                U_infty = acoustic_case.U
            else:
                U_infty = Uinf_BL_zero
            for axis in [ax[0],ax[1]]:
                axis.scatter(
                    acoustic_case.alpha,
                    Strouhal(
                        acoustic_case.crossover,
                        delta_zero.values[0],
                        U_infty
                    ),
                **plot_args
                )
            if not article:
                ax[2].scatter(
                    acoustic_case.alpha,
                    Strouhal(
                        acoustic_case.crossover,
                        delta_zero.values[0]*2,
                        U_infty
                    ),
                    **plot_args
                )
        print "{0:.2f}".format(U_infty*100/acoustic_case.U)
    ax[-1].set_xticks([0,6,12])
    ax[-1].set_xlabel("$\\alpha_g$ [deg]")
    if not article:
        ax[1].set_ylabel("$\\mathrm{St}=f_0\\delta_{95}/U_\\infty$")
    else:
        ax[0].text(
            -0.13,
            -0.1,
            "$\\mathrm{St}=f_0\\delta_{95}/U_\\infty$",
            transform=ax[0].transAxes,
            ha='center',
            va='center',
            fontsize=19,
            rotation=90
        )
    ax[1].legend(fontsize=18,loc='lower left')
    if not article:
        ax[0].text(0.95, 1.00, '$\\varphi = 6^\\circ$',
                   horizontalalignment='right',
                   verticalalignment='bottom',
                   transform=ax[0].transAxes,
                   fontsize=18
                  )
    ax[0].text(0.01, 1.0, '$\\delta_{95,\\;\\mathrm{suction\\; side}}$',
               horizontalalignment='left',
               verticalalignment='bottom',
               transform=ax[0].transAxes,
               fontsize=18
              )
    ax[1].text(0.01, 1.0, '$\\delta_{95,\\;\\mathrm{pressure\\; side}}$',
               horizontalalignment='left',
               verticalalignment='bottom',
               transform=ax[1].transAxes,
               fontsize=18
              )
    if not article:
        ax[2].text(0.01, 1.0, '$\\delta_{\\mathrm{suction\, side}}+\\delta_{\\mathrm{pressure\, side}}$',
                   horizontalalignment='left',
                   verticalalignment='bottom',
                   transform=ax[2].transAxes
                  )
    if article:
        plt.savefig('./article_images/Crossover_Strouhal_and_AoA.png',
                    bbox_inches='tight')
    else:
        plt.savefig('Crossover_Strouhal_and_AoA.png',bbox_inches='tight')
    plt.close()




