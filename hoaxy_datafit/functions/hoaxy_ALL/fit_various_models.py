#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import packages
import numpy as np
import matplotlib.pyplot as pp
import pylab
import scipy
import pandas as pd
from scipy.optimize import curve_fit
import pickle
from models_functions import mf_noseg, mf_noseg_BA, mf_noseg_FA
from fit_functions import fit_mf_noseg

# import model and curvefit functions
# from models_functions import mf_noseg
# from fit_functions import fit_mf_noseg

# list of files
list_of_files=['hoaxy_4th-mysterious-death-connected-to-the-dnc_cum','hoaxy_alicia-machado-adult-star_cum','hoaxy_bill-clinton-illegitimate-son_cum','hoaxy_black-lives-matter-protesters-chant-for-dead-cops-now-in-baton-rouge_cum','hoaxy_black-protesters-targeted-whites-in-milwaukee_cum','hoaxy_clinton-byrd-photo-klan_cum','hoaxy_clinton-compliant-citizenry_cum','hoaxy_clinton-secret-earpiece-debate_cum','hoaxy_clintons_zeifman_cum','hoaxy_debate-secret-hand-signals_cum','hoaxy_deray-mckesson-and-the-summer-of-chaos_cum','hoaxy_dnc-hiring-actors-via-craigslist-to-replace-delegates_cum','hoaxy_dr-drew-hillary-clinton-health_cum','hoaxy_flags-banned-at-dnc_cum','hoaxy_google-manipulate-hillary-clinton_cum','hoaxy_hillary-clinton-freed-child-rapist-laughed-about-it_cum','hoaxy_hillary-clinton-has-parkinsons-disease_cum','hoaxy_hillary-clinton-medical-records-leaked_cum','hoaxy_hillary-clinton-seizure-video_cum','hoaxy_julian-assange-bernie-sanders-was-threatened_cum','hoaxy_khizr-khan-375000-clinton-foundation_cum','hoaxy_khizr-khan-is-a-muslim-brotherhood-agent_cum','hoaxy_mexico-border-trump-elected_cum','hoaxy_michael-savage-removed_cum','hoaxy_muslims-in-japan_cum','hoaxy_politics-sites-mismatched-clinton-rally-image-goes-viral_cum','hoaxy_satire_sharia_cum','hoaxy_seth-conrad-rich_cum','hoaxy_three-syrian-refugees-assault-5-year-old-girl-at-knifepoint_cum','hoaxy_tim-kaine-white-people-minority_cum','hoaxy_yokohillary_cum']
path_file = "../../data/"

# threshold for when a contagion is said to have plateaud
plateau_threshold = 48;


noseg_fit_popt = [];
noseg_fit_pcov = [];
noseg_fit_RMSerror = [];
noseg_fit_NRMSerror = [];
noseg_fit_MPerror = [];

for i in np.linspace(0,len(list_of_files)-1,len(list_of_files),dtype=int):
    
    if i == 1: break;
    
    # READ DATA
    
    file_name = str(list_of_files[i])
    hoax_data = pd.read_csv(path_file+file_name+'.csv',parse_dates=True)
    for_users = hoax_data["For"]
    against_users = hoax_data["Against"]
    t_empirical=np.arange(0,len(for_users))
    
    # FILTER DATA
    
    # remove the initial plateau from the data
    first_nonzero = np.nonzero(for_users)[0][0]
    for_users = for_users[first_nonzero:]
    against_users = against_users[first_nonzero:]
    
    # find the position of the end of the dynamics (including buffer plateau at end of length plateau_threshold)
    d_for_users = np.subtract(for_users[plateau_threshold-1:],for_users[0:-plateau_threshold+1]);
    d_against_users = np.subtract(against_users[plateau_threshold-1:],against_users[0:-plateau_threshold+1]);
    plateau = np.nonzero((np.add(d_for_users,d_against_users))==0)[0];
    if (plateau.size > 0):
        temporal_window = plateau[0] + plateau_threshold
        for_users = for_users[0:temporal_window]
        against_users = against_users[0:temporal_window]
    
    t_empirical=np.arange(0,len(for_users))
    
    # CURVEFIT AND PLOT
    
    #params = [alpha, ONEoverN, pv,    tauINV, ba_init, bi_init, fa_init, fi_init]
    param0 =   0.5,   0.0001,   0.001, 0.001,  for_users.values[0], 0.0, against_users.values[0], 0.0
    param_bounds =([0., 0., 0, 0., for_users.values[0], 0., against_users.values[0], 0.],
                   [1., 1., 1., 1., for_users.values[0]+0.0001 ,0.0001, against_users.values[0]+0.0001, 0.0001])
    
    # Curve fit
    T_double = np.append(t_empirical, t_empirical)
    data_double = np.append(for_users, against_users)
    popt, pcov = curve_fit(fit_mf_noseg, T_double, data_double, p0=param0,bounds=param_bounds, max_nfev=10000)
    
    # Save measurements
    noseg_fit_popt.append(popt)
    noseg_fit_pcov.append(pcov)
    BA, FA = mf_noseg(t_empirical,*popt)
    noseg_fit_RMSerror.append(np.sqrt(np.sum(np.square(np.append(BA,FA) - data_double))/len(data_double)))
    noseg_fit_NRMSerror.append(np.sqrt(np.sum(np.square(np.append(BA,FA) - data_double))/len(data_double))/np.average(data_double))
    noseg_fit_MPerror.append(np.sum(np.abs(np.append(BA,FA) - data_double)/data_double)/len(data_double))
    
    # Plot
    pp.figure()
    pp.plot(t_empirical/24., for_users, 'b+',t_empirical/24.,
            BA,'b-', t_empirical/24., against_users, 'r+',t_empirical/24.,
            FA,'r-')
    pp.xlabel("t (days)")
    pp.ylabel("# Active on day t")
    pp.title(file_name)
    pp.legend(['FOR data', 'FOR model','AGAINST data', 'AGAINST model'],loc=0)
    #pp.savefig("../../output/hoaxy_ALL/fits/"+str(i+1)+"_noseg.pdf")
    pp.show()

f = open(path_file + "processed/RMSerror_basic.pckl","wb");
pickle.dump(noseg_fit_RMSerror, f)
f.close()

