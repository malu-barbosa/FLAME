from main import *
from   libs.plot_AR6_hexagons import *
from   libs.NME import *
from libs.flatten_list import *
from libs.time_series_comparison import *
import numpy  as np
import matplotlib.pyplot as plt
from pdb import set_trace
import os


if __name__=="__main__":
    
    filename_model = "/scratch/hadea/isimip3a/u-cc669_isimip3a_fire/20CRv3-ERA5_obsclim/jules-vn6p3_20crv3-era5_obsclim_histsoc_default_burntarea-total_global_monthly_1901_2021.nc"

    dir_observation = "/data/dynamic/dkelley/fireMIPbenchmarking/data/benchmarkData/"
    filenames_observation = ["ISIMIP3a_obs/GFED4.1s_Burned_Fraction.nc", \
                             "ISIMIP3a_obs/FireCCI5.1_Burned_Fraction.nc", \
                             "ISIMIP3a_obs/GFED500m_Burned_Percentage.nc"]
    filenames_observation = [dir_observation + file for file in filenames_observation]

    year_range = [1996, 2020]
    ar6_regions =  regionmask.defined_regions.ar6.land.region_ids
    n_itertations = 1000
    tracesID = 'burnt_area_u-cc669'
    
    output_file = 'outputs/trend_burnt_area_metric_results.csv'
    
    def trend_prob_for_region(ar6_region_code, value):# in ar6_regions:   
     
        if not isinstance(ar6_region_code, str): return 
        if ar6_region_code == 'EAN' or ar6_region_code == 'WAN': return
        if len(ar6_region_code) > 5: return
        print(ar6_region_code)
        subset_functions = [sub_year_range, ar6_region, make_time_series]
        subset_function_args = [{'year_range': year_range},
                            {'region_code' : [ar6_region_code]}, 
                            {'annual_aggregate' : iris.analysis.SUM}]
        
        tracesID_save = 'temp/eval_trends' + tracesID + '-' + \
                            'REGION---' + ar6_region_code + '---' + \
                            '_'.join([str(year) for year in year_range])
        
        
        Y_temp_file = tracesID_save + '-Y' + '.npy'
        X_temp_file = tracesID_save + '-X' + '.npy'
        if os.path.isfile(Y_temp_file) and os.path.isfile(X_temp_file): 
            Y = np.load(Y_temp_file)
            X = np.load(X_temp_file)
        else :
            Y, X = read_all_data_from_netcdf(filename_model, filenames_observation, 
                                             time_series = year_range, check_mask = False,
                                             subset_function = subset_functions, 
                                             subset_function_args = subset_function_args)
            np.save(Y_temp_file, Y)  
            np.save(X_temp_file, X)
        
        gradient_compare = find_and_compare_gradients(Y, X, tracesID_save, 
                                                      n_itertations = n_itertations)
        
        #NME_temp_file =
        #    'temp/eval_trendsburnt_area_u-cc669-REGION---GIC---1996_2020-NME-nObs_3.npy'
        nme = NME(X, Y)        
        nme_null = NME_null(X)
        obs_mean = np.nanmean(X, axis = 0)

        Yspread = np.reshape(np.repeat(Y, X.shape[1]), X.shape)
        Yspread[np.isnan(X)] = np.nan
        mod_mean = np.nanmean(Yspread, axis = 0)
        
        
        out =  ar6_region_code, value, obs_mean, mod_mean, nme
        out = [out[0], out[1]] + list(np.concatenate(out[2:4])) + \
               list(out[4].values.flatten()) + list(nme_null.values.flatten()) + \
               list(gradient_compare.values.flatten())
        
        return(out)

    models = [str(i) for i in range(len(filenames_observation))] + ['All']
    null_models = ['Median', 'Mean', 'Randomly-resampled mean', 'Randomly-resampled - sd']
    index = ['Region Code', 'Region ID'] + \
            ['observation ' + str(i) for i in range(len(filenames_observation))] + \
            ['simulations ' + str(i) for i in range(len(filenames_observation))] + \
            [['NME ' + j + ' obs. ' + i for i in models] for j in ['1', '2', '3', 'A']]  + \
            [[j + 'Null model obs. ' + i for i in models] for j in null_models] + \
            ['Gradient overlap', 'Obs trend - 10%', 'Obs trend - 90%', 
                                  'Mod trend - 10%', 'Mod trend - 90%']
    index = flatten_list(index)
    
    result = list(map(lambda item: trend_prob_for_region(item[0], item[1]), \
                                    ar6_regions.items()))
    result = list(filter(lambda x: x is not None, result))

    result = pd.DataFrame(np.array(result).T, index = index, columns = np.array(result)[:,0])
    result.to_csv(output_file)
    plot_AR6_hexagons(result, resultID = 2, colorbar_label = 'Gradient Overlap')
    plt.show()
  

    
#"/"

#"GFED4.nc", "MCD45.nc", "meris_v2.nc"
