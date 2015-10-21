def plot_gruber_strouhals():
    from matplotlib import pyplot as plt
    import pandas as pd
    import seaborn as sns
    from matplotlib import rc
    from numpy import array,argmin,unique

    rc('text',usetex=True)

    sns.set_context('paper')
    sns.set_style("whitegrid")
    sns.set(font='serif',font_scale=2.5,style='whitegrid')
    rc('font',family='serif', serif='cm10')

    strouhal_key = "$\\mathrm{St}_0=f_0\\delta/U_\\infty$"
    ratio_key    = "$\\lambda/h$"

    markers = [
            u'o', u'v', u'^', u'<', u'>', u'8', u's', u'p', u'*', 
        u'h', u'H', u'D', u'd'
    ]

    gruber_strouhals = [
        1.18,
        1.,
        1.35,
        1.35,
        1.4,
        1.45,
    ]
    gruber_ratios = [
        0.1,
        0.15,
        0.2,
        0.3,
        0.5,
        0.6,
    ]

    gruber_lengths = array([
        30,20,30,20,20,30,
    ])

    gruber_lambdas = array([
        1.5,1.5,3,3,5,9
    ])

    palette = sns.color_palette("cubehelix", 
                                n_colors=len(unique(gruber_lambdas))
                               )

    grouber_results_df = pd.DataFrame(
        columns=[ strouhal_key, ratio_key ]
    )

    for st,r,leng,lambd in zip(gruber_strouhals,gruber_ratios,
                         gruber_lengths,gruber_lambdas):
        grouber_results_df = grouber_results_df.append(
            {
                strouhal_key : st,
                ratio_key    : r,
                'length'     : leng,
                'lambda'     : lambd,
            },
            ignore_index=True
        )

    fig,ax = plt.subplots(1,1)
    plot_options = {
        's'      : 100,
        #'marker' : 's'
    }
    done_length = []
    done_lambda = []
    for index,row in grouber_results_df.iterrows():
        length_identifying_key = argmin( 
                abs(unique(gruber_lengths) - row.length) 
            ) 
        lambda_identifying_key = argmin( 
                abs(unique(gruber_lambdas) - row['lambda']) 
            ) 
        if row.length not in done_length:
            length_label = "$2h = {{{0}}}$ mm".format(row.length)
            done_length.append(row.length)
        else:
            length_label = '' 
        if row['lambda'] not in done_lambda:
            lambda_label = "$\\lambda = {{{0}}}$ mm".format(
                row['lambda']
            )
            done_lambda.append(row['lambda'])
        else:
            lambda_label = '' 
        ax.scatter(
            y      = row[strouhal_key],
            x      = row[ratio_key],
            c      = palette[lambda_identifying_key],
            #marker = markers[length_identifying_key],
            marker = markers[0],
            label  = lambda_label,
            **plot_options
        )
    print done_length
    ax.set_ylabel(strouhal_key)
    ax.set_xlabel(ratio_key)
    ax.legend(loc='lower right')
    plt.savefig('Gruber_Results.png',bbox_inches='tight')


def move_all_acoustic_data_to_local():
    import os
    import acoustic_functions as afunc

    destination = './AcousticData'
    acoustic_root = \
            '/media/carlos/6E34D2CD34D29783/2015-03_SerrationAcoustics/'
    acoustic_campaign = 'MarchData'

    acoustic_data_path = os.path.join(acoustic_root,acoustic_campaign)

    acoustic_cases = [f for f\
                      in os.listdir(acoustic_data_path)\
                      if os.path.isdir(
                          os.path.join(acoustic_data_path,f)
                      )]

    for ac in acoustic_cases:
        afunc.move_data_to_local(
            os.path.join(acoustic_data_path,ac),
            os.path.join(destination,"psd_"+ac+'.mat')
        )
