import sys
sys.path.append('fire_model/')
sys.path.append('libs/')

from MaxEntFire import MaxEntFire

from BayesScatter import *
#from train import *

from read_variable_from_netcdf import *
from combine_path_and_make_dir import * 
from pymc_extras import select_post_param
from plot_maps import *
import os
from   io     import StringIO
import numpy  as np
import pandas as pd
import math
from scipy.special import logit, expit

import matplotlib.pyplot as plt
import arviz as az

from scipy.stats import wilcoxon

def runSim_MaxEntFire(params, X, eg_cube, id_name, dir_samples, run_name, grab_old_trace):  
    def sample_model(i, run_name = 'control'):   
        dir_sample =  combine_path_and_make_dir(dir_samples, run_name)
        file_sample = dir_sample + '/sample' + str(i) + '.nc'
        
        if os.path.isfile(file_sample) and grab_old_trace:
            return iris.load_cube(file_sample)
        print("Generating Sample:" + file_sample)
        param_in = [param[i] if param.ndim == 1 else param[i,:] for param in params]
        param_in = dict(zip(params_names, param_in))
        out = MaxEntFire(param_in).burnt_area(X)
        out = insert_data_into_cube(out, eg_cube, lmask)
        coord = iris.coords.DimCoord(i, "realization")
        out.add_aux_coord(coord)
        iris.save(out, file_sample)
        
        return out

    nits = len(trace.posterior.chain)*len(trace.posterior.draw)
    idx = range(0, nits, int(np.floor(nits/sample_for_plot)))
    out = np.array(list(map(lambda id: sample_model(id, id_name), idx)))

    return iris.cube.CubeList(out).merge_cube()


def compare_to_obs_maps(filename_out, dir_outputs, Obs, Sim, lmask, levels, cmap):    
    ax = plt.subplot(2, 3, 4)
    BayesScatter(Obs, Sim, lmask,  0.000001, 0.000001, ax)
    plot_BayesModel_maps(Sim, lmask, levels, cmap, Obs, Nrows = 2, Ncols = 3)
    
    X = Obs.data.flatten()[lmask]
    ncells = int(len(X)/Obs.shape[0])
    X = X.reshape([Obs.shape[0], ncells])
    Y = [Sim[i].data.flatten()[lmask].reshape([Obs.shape[0],ncells]) \
         for i in range(Sim.shape[0])]
    Y = np.array(Y)
   
    pos = np.mean(X[np.newaxis, :, :] > Y, axis = 0)
    _, p_value = wilcoxon(pos - 0.5, axis = 0)
    apos = np.mean(pos, axis = 0)
    
    mask = lmask.reshape([ X.shape[0], int(lmask.shape[0]/X.shape[0])])[0]
    apos_cube = insert_data_into_cube(apos, Obs[0], mask)
    p_value_cube = insert_data_into_cube(p_value, Obs[0], mask)
    
    plot_annual_mean(apos_cube,[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], 
                     'RdYlBu_r',  plot_name = "mean bias",  Nrows = 2, Ncols = 3, plot_n = 5)

    plot_annual_mean(p_value_cube, np.array([0, 0.01, 0.05, 0.1, 0.5, 1.0]), 'copper',   
                     plot_name = "mean bias p-value",   Nrows = 2, Ncols = 3, plot_n = 6)
    
    plt.gcf().set_size_inches(12, 8)

    fig_dir = combine_path_and_make_dir(dir_outputs, '/figs/')

    plt.savefig(fig_dir + filename_out + '-evaluation.png')


def plot_parameter_info(traces, fig_dir, filename):
    """ plots parameter distributions from a trace file.
    More info to follow
    """
    az.plot_trace(trace)
    plt.savefig(fig_dir + filename + '-traces.png')


def evaluate_MaxEnt_model(trace, y_filen, x_filen_list, scalers, CA_filen = None, dir = '', 
                         dir_outputs = '', model_title = '', filename_out = '',
                         subset_function = None, subset_function_args = None,
                         sample_for_plot = 1, grab_old_trace = False,
                         *args, **kw):

    """ Runs prediction and evalutation of the sampled model based on previously run trace.
    Arguments:
        trace - pymc traces nc or nc fileiles, probably from a 'train_MaxEnt_model' run
	y_filen -- filename of dependant variable (i.e burnt area)
        x_filen_list -- filanames of independant variables
	scalers -- the scalers used during the generation of the trace file that scales 
            x data between 0 and 1 (not that it might not scale the opened variables 
            here between 0 and 1 as different data maybe selected for evaluation). 
            can be csv filename.
        dir -- dir y_filen and  x_filen_list are stored in. default it current dir
        dir_outputs -- directiory where all outputs are stored. String
        model_title - title of model run. A str default to 'no_name'. Used to initially to name 
                the dir everythings stored in.
        filename_out -- string of the start of the traces output name. Detault is blank. 
		Some metadata will be saved in the filename, so even blank will 
                save a file.
        subset_function -- a list of constrain function useful for constraining and resticting 
                data to spatial locations and time periods/months. Default is not to 
                constrain (i.e "None" for no functions")
        subset_function_args -- list of arguements that feed into subset_function
        sample_for_plot -- fraction of gridcells used for optimization
        grab_old_trace -- Boolean. If True, and a filename starting with 'filename' and 
                containing some of the same setting (saved in filename) exists,  it will open 
                and return this rather than run new samples. Not all settings are saved for 
                identifiation, so if in doubt, set to 'False'.
	*args, **kw -- arguemts passed to 'evaluate_model' and 'project_model'
    
    Returns:
        look in dir_outputs + model_title, and you'll see figure and tables from evaluation, 
        projection, reponse curevs, jacknifes etc (not all implmenented yet)
    """

    common_args = {
        'y_filename': y_filen,
        'x_filename_list': x_filen_list,
        'add_1s_columne': True,
        'dir': dir,
        'x_normalise01': True,
        'subset_function': subset_function,
        'subset_function_args': subset_function_args
    }

    if CA_filen is not None:
        Y, X, lmask, scalers, CA = read_all_data_from_netcdf(CA_filename = CA_filen, **common_args)   
    else:
        Y, X, lmask, scalers = read_all_data_from_netcdf(**common_args)
    
    Obs = read_variable_from_netcdf(y_filen, dir,
                                    subset_function = subset_function, 
                                    subset_function_args = subset_function_args)
    
    params = select_post_param(trace)  
    
    dir_outputs = combine_path_and_make_dir(dir_outputs, model_title)
    dir_samples = combine_path_and_make_dir(dir_outputs, '/samples/')     
    dir_samples = combine_path_and_make_dir(dir_samples, filename_out)
      
    Sim = runSim_MaxEntFire(params, X, Obs, id_name, dir_samples, 
                            run_name, grab_old_trace, "control") 

    standard_response_curve(Sim, X, Obs, id_name, dir_samples, 
                            run_name, grab_old_trace)
        
          
    sensitivity_reponse_curve(Sim, X, Obs, id_name, dir_samples, 
                            run_name, grab_old_trace)
    

    compare_to_obs_maps(filename_out, dir_outputs, Obs, Sim, lmask, *args, **kw)



if __name__=="__main__":
    """ Running optimization and basic analysis. 
    Variables that need setting:
    For Optimization:
        model_title -- name of model run. Used as directory and filename.
        trace_file -- netcdf filename containing trace (produced in pymc_MaxEnt_train.py)
        y_filen -- filename of dependant variable (i.e burnt area)
        x_filen_list -- filanames of independant variables
            (ie bioclimate, landscape metrics etc)
        months_of_year --- which months to extact on training and projecting
        dir_outputs -- where stuff gets outputted
        dir_projecting -- The directory of the data used for prjections. 
            Should contain same files for independant varibales as dir_training 
            (though you should be able to adpated this easily if required). 
            Doesnt need dependant variable, but if there, this will (once
            we've implmented it) attempt some evaluation.
        sample_for_plot -- how many iterations (samples) from optimixation should be used 
            for plotting and evaluation.
        levels -- levels on the colourbar on observtation and prodiction maps
        cmap -- levels on the colourbar on observtation and prodiction maps
    Returns:
         (to be added too)
    """

    """ 
        SETPUT 
    """
    ### input data paths and filenames
    model_title = 'simple_example_model'
    
    trace_file = "outputs//trace-trees_consec_dry_mean_crop_pas_humid_totalVeg-frac_points_0.01-Month_7-nvariables_-frac_random_sample0.01-nvars_6-niterations_100.nc"
    scaler_file = "outputs//scalers-trees_consec_dry_mean_crop_pas_humid_totalVeg-frac_points_0.01-Month_7-nvariables_-frac_random_sample0.01-nvars_6-niterations_100.csv"
   
    y_filen = "GFED4.1s_Burned_Fraction.nc"
    CA_filen = None
    x_filen_list=["trees.nc","consec_dry_mean.nc",
                  "crop.nc", "pas.nc", "humid.nc", "totalVeg.nc"] 
    
    
    months_of_year = [7]
    
    """ Projection/evaluating """
    dir_outputs = 'outputs/'

    dir_projecting = "../ConFIRE_attribute/isimip3a/driving_data/GSWP3-W5E5-20yrs/Brazil/AllConFire_2000_2009/"

    sample_for_plot = 20

    levels = [0, 0.1, 1, 2, 5, 10, 20, 50, 100] 
    cmap = 'OrRd'

    
    subset_function = sub_year_months
    subset_function_args = {'months_of_year': months_of_year}

    """ 
        RUN evaluation 
    """
    evaluate_MaxEnt_model(trace, y_filen, x_filen_list, scalers, CA_filen, dir_projecting,
                         dir_outputs, model_title, filename,
                         subset_function, subset_function_args,
                         sample_for_plot, 
                         run_evaluation = run_evaluation, run_projection = run_projection,
                         grab_old_trace = grab_old_trace,
                         levels = levels, cmap = cmap)
    
    