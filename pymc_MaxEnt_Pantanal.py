from pymc_MaxEnt import *

if __name__=="__main__":
    """ Running optimization and basic analysis. 
    Variables that need setting:
    For Optimization:
        dir_training -- The directory of the training data inclduing 
            dependant and independant variables
        y_filen -- filename of dependant variable (i.e burnt area)
        x_filen_list -- filanames of independant variables
            (ie bioclimate, landscape metrics etc)
        cores - how many chains to start (confusiong name, I know).
            When running on slurm, also number of cores
        fraction_data_for_sample -- fraction of gridcells used for optimization
        niterations -- number of iterations or samples )after warm-up) in optimization for each
            chain. Equivalent to number of ensemble members.
        months_of_year --- which months to extract on training and projecting
        grab_old_trace -- Boolean. If True and there's an appropriate looking old trace file, 
            then  optimisation is skipped that file is loaded instead. 
            This isn't totally infallible, so if doing a final run and in doubt, set to False
    For Projection/evaluating:
        dir_outputs -- where stuff gets outputted
        dir_projecting -- The directory of the data used for projections. 
            Should contain same files for independant variables as dir_training 
            (though you should be able to adpat this easily if required). 
            Doesnt need dependant variable, but if there, this will (once
            we've implemented it) attempt some evaluation.
        sample_for_plot -- how many iterations (samples) from optimization should be used 
            for plotting and evaluation.
        levels -- levels on the colourbar on observation and prediction maps
        cmap -- levels on the colourbar on observattion and prediction maps
    Returns:
        trace file, maps, etc (to be added too)
    """

    """ 
        SETPUT 
    """
    """ optimization """

    model_title = 'Pantanal_model4'

    dir_training = "/data/users/douglas.kelley/MaxEnt/driving_Data/Pantanal_paper/"
    #y_filen = "GFED4.1s_Burned_Fraction.nc"
    y_filen = "Area_Burned_NAT_pant.nc"
    #"MPA.nc", "TCA.nc", "E_density.nc"
    CA_filen = "brazil_NAT.nc"

    x_filen_list=["precip.nc", "tas_max.nc", "csoil.nc", 
                  "cveg.nc", "forest.nc", "savanna.nc", "grassland.nc", 
                  "cropland.nc", "pasture.nc", "wetland.nc"]

    grab_old_trace = True
    cores = 4
    fraction_data_for_sample = 0.5
    niterations = 1000
    #ASO
    months_of_year = [7, 8, 9]

    response_grouping = [["precip.nc", "tas_max.nc"], 
                         ["wetland.nc", "grassland.nc"],
                         ["wetland.nc", "precip.nc"]]     

    """ Projection/evaluating """
    dir_outputs = 'outputs/'

    dir_projecting = dir_training

    sample_for_plot = 100

    
    levels = [0, 0.1, 1, 2, 5, 10, 20, 50, 100] 
    dlevels = [-20, -10, -5, -2, -1, -0.1, 0.1, 1, 2, 5, 10, 20]
    cmap = 'OrRd'
    dcmap = 'RdBu_r'

    run_evaluation = True
    run_projection = True
    
    """ 
        RUN optimization 
    """
    subset_function = [sub_year_months, constrain_BR_biomes]
    subset_function_args = [{'months_of_year': months_of_year}, {'biome_ID': [6]}]

    filename = '_'.join([file[:-3] for file in x_filen_list]) + \
              '-frac_points_' + str(fraction_data_for_sample) + \
              '-Month_' +  '_'.join([str(mn) for mn in months_of_year])

    #### Optimize
    trace, scalers, variable_info_file = train_MaxEnt_model(y_filen, x_filen_list, CA_filen, 
                                        dir_training, 
                                        filename, dir_outputs,
                                        fraction_data_for_sample,
                                        subset_function, subset_function_args,
                                        niterations, cores, model_title, '', grab_old_trace)
    
    """ 
        RUN projection 
    """
    '''predict_MaxEnt_model(trace, y_filen, x_filen_list, scalers, dir_projecting,
                         dir_outputs, model_title, filename,
                         subset_function, subset_function_args,
                         sample_for_plot, 
                         run_evaluation = run_evaluation, run_projection = run_projection,
                         grab_old_trace = grab_old_trace,
                         levels = levels, cmap = cmap) 
    '''
    evaluate_MaxEnt_model_from_namelist(variable_info_file, 
                                        subset_function_args = subset_function_args, 
                                        dir = dir_projecting,
                                        grab_old_trace = grab_old_trace,
                                        sample_for_plot = sample_for_plot,
                                        levels = levels, cmap = cmap,
                                        dlevels = dlevels, dcmap = dcmap,
                                        response_grouping = response_grouping)
