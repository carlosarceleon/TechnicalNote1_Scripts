import acoustic_functions as acfunc
import bl_functions as blfunc
import os

acoustic_root = \
        '/media/carlos/6E34D2CD34D29783/2015-03_SerrationAcoustics/'
acoustic_campaign = 'MarchData'

acoustic_data_path = os.path.join(acoustic_root,acoustic_campaign)

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
        return "{0}_a{1:02d}_p{2}_U{3}".\
                format(
                    device,
                    alpha,
                    phi,
                    speed
                )
    if "July" in campaign:
        return "{0}_a{1}_U{2}".\
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
                            acoustic_root,campaign),
                        case=case_name,
                        relative_to=ste_case_name,
                        campaign='MarchData'
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

def plot_bl_crossover_relation():
    import matplotlib.pyplot as plt 
    from numpy import array,argmin
    import seaborn as sns


    crossover_df = get_crossovers()
    bl_df        = get_boundary_layers()
    flatui = ["#3498db", "#95a5a6", "#e74c3c"]

    colormap = sns.color_palette(
        flatui,
        len(bl_df.U.unique())
    )

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
            delta_sum  = delta_ps.values[0]+delta_ss.values[0]
        else: delta_sum = array([])

        color = colormap[
            argmin(map(abs,delta.U.values[0]-bl_df.U.unique()))
        ]
        marker_size = 200
        alpha = 0.7

        if delta.U.values[0] in done_labels:
            label = ''
        else:
            label = "$U_\\infty = {{{0}}}$ [m/s]".format(
                acoustic_case.U
            )
            done_labels.append(delta.U.values[0])


        plot_args = {
            'c'     : color,
            'alpha' : alpha,
            's'     : marker_size,
            'label' : label
        }

        # Presure side delta plot
        if delta_ps.shape[0]:
            ax[0].scatter(
                acoustic_case.alpha,
                Strouhal(
                    acoustic_case.crossover,
                    delta_ps.values[0],
                    acoustic_case.U
                ),
                **plot_args
            )
        if delta_ss.shape[0]:
            ax[1].scatter(
                acoustic_case.alpha,
                Strouhal(
                    acoustic_case.crossover,
                    delta_ss.values[0],
                    acoustic_case.U
                ),
                **plot_args
            )

            ax[2].scatter(
                acoustic_case.alpha,
                Strouhal(
                    acoustic_case.crossover,
                    delta_sum,
                    acoustic_case.U
                ),
                **plot_args
            )

        if delta_zero.shape[0]:
            for axis in [ax[0],ax[1]]:
                axis.scatter(
                    acoustic_case.alpha,
                    Strouhal(
                        acoustic_case.crossover,
                        delta_zero.values[0],
                        acoustic_case.U
                    ),
                **plot_args
                )
            ax[2].scatter(
                acoustic_case.alpha,
                Strouhal(
                    acoustic_case.crossover,
                    delta_zero.values[0]*2,
                    acoustic_case.U
                ),
                **plot_args
            )
    ax[-1].set_xticks([0,6,12])
    ax[-1].set_xlabel("$\\alpha_g$ [deg]")
    ax[1].set_ylabel("$\\mathrm{St}=f\\delta_{95}/U_\\infty$")
    ax[0].legend()
    ax[0].text(0.95, 1.00, '$\\varphi = 6^\\circ$',
               horizontalalignment='right',
               verticalalignment='bottom',
               transform=ax[0].transAxes
              )
    ax[0].text(0.01, 1.0, '$\\delta_{\\mathrm{suction\, side}}$',
               horizontalalignment='left',
               verticalalignment='bottom',
               transform=ax[0].transAxes
              )
    ax[1].text(0.01, 1.0, '$\\delta_{\\mathrm{pressure\, side}}$',
               horizontalalignment='left',
               verticalalignment='bottom',
               transform=ax[1].transAxes
              )
    ax[2].text(0.01, 1.0, '$\\delta_{\\mathrm{suction\, side}}+\\delta_{\\mathrm{pressure\, side}}$',
               horizontalalignment='left',
               verticalalignment='bottom',
               transform=ax[2].transAxes
              )
    plt.savefig('Crossover_Strouhal_and_AoA.png')
    plt.close()




