#!/usr/bin/env python
# encoding: utf-8
import matplotlib
matplotlib.use('Agg')
list_of_files=['hoaxy_4th-mysterious-death-connected-to-the-dnc_cum','hoaxy_alicia-machado-adult-star_cum','hoaxy_bill-clinton-illegitimate-son_cum','hoaxy_black-lives-matter-protesters-chant-for-dead-cops-now-in-baton-rouge_cum','hoaxy_black-protesters-targeted-whites-in-milwaukee_cum','hoaxy_clinton-byrd-photo-klan_cum','hoaxy_clinton-compliant-citizenry_cum','hoaxy_clinton-secret-earpiece-debate_cum','hoaxy_clintons_zeifman_cum','hoaxy_debate-secret-hand-signals_cum','hoaxy_deray-mckesson-and-the-summer-of-chaos_cum','hoaxy_dnc-hiring-actors-via-craigslist-to-replace-delegates_cum','hoaxy_dr-drew-hillary-clinton-health_cum','hoaxy_flags-banned-at-dnc_cum','hoaxy_google-manipulate-hillary-clinton_cum','hoaxy_hillary-clinton-freed-child-rapist-laughed-about-it_cum','hoaxy_hillary-clinton-has-parkinsons-disease_cum','hoaxy_hillary-clinton-medical-records-leaked_cum','hoaxy_hillary-clinton-seizure-video_cum','hoaxy_julian-assange-bernie-sanders-was-threatened_cum','hoaxy_khizr-khan-375000-clinton-foundation_cum','hoaxy_khizr-khan-is-a-muslim-brotherhood-agent_cum','hoaxy_mexico-border-trump-elected_cum','hoaxy_michael-savage-removed_cum','hoaxy_muslims-in-japan_cum','hoaxy_politics-sites-mismatched-clinton-rally-image-goes-viral_cum','hoaxy_satire_sharia_cum','hoaxy_seth-conrad-rich_cum','hoaxy_three-syrian-refugees-assault-5-year-old-girl-at-knifepoint_cum','hoaxy_tim-kaine-white-people-minority_cum','hoaxy_yokohillary_cum']

for item in list_of_files:
	print item
	file_name=str(item)
	print file_name+'_day.csv'
	path_figs='/webofscience/diego/fitting_by_hour/figs_saturation/'
	path_file_hours='/webofscience/diego/fitting_by_hour/hours_saturation/'
	path_file_days='/webofscience/diego/fitting_by_hour/days/'
	def mf_noseg(T, alpha, ONEoverN, ba_init, bi_init, pv, omega):
        
	    # Network size
	    N=1./ONEoverN
        
	    # Initial conditions
	    pBI0, pBA0, pFI0, pFA0, pS0 = N*bi_init, N*ba_init, 0.0, 0.0, N - N*ba_init - N*bi_init
	    
	    ba = []
	    fa = []
	    for i in T:
            
	        ba.append(pBA0)
	        fa.append(pFA0)
	        
	        f = pBA0/N
	        pBI1 = alpha * f * pS0 + omega * pBA0 + (1. - pv) * (1 - f) * pBI0
	        pBA1 = (1. - pv) * f  * pBI0 + (1. - omega) * (1. - pv) * pBA0
	        pFI1 = (1-alpha) * f * pS0 + omega * pFA0 + pv * (pBI0 + (1. - omega) * pBA0) + (1 - f) * pFI0
	        pFA1 = f * pFI0 + (1. - omega) * pFA0
	        pS1 = (1 - f) * pS0
            
	        #update
	        pBI0, pBA0, pFI0, pFA0, pS0 = pBI1, pBA1, pFI1, pFA1, pS1
            
	        if float(pBI0)<=0.0000000001:
	            pBI0=0.0
	        if float(pBA0)<=0.0000000001:
	            pBA0=0.0
	        if float(pFI0)<=0.0000000001:
	            pFI0=0.0
	        if float(pFA0)<=0.0000000001:
	            pFA0=0.0
	        if float(pS0)<=0.0000000001:
	            pS0=0.0
        
	    return np.cumsum(np.asarray(ba)), np.cumsum(np.asarray(fa))
    
	# To return only one of the types (needed for fitting only against one type)
	def mf_noseg_BA(T, alpha, ONEoverN, ba_init, bi_init, pv, omega):
	    return mf_noseg(T, alpha, ONEoverN, ba_init, bi_init, pv, omega)[0]
    
	def mf_noseg_FA(T, alpha, ONEoverN, ba_init, bi_init, pv, omega):
	    return mf_noseg(T, alpha, ONEoverN, ba_init, bi_init, pv, omega)[1]
    
    
    
	# Mean-field model with segregation (two clusters gullible-skeptic)
	def mf_seg(T, alphag, alphas, ONEoverN, ba_init, bi_init, pvg, pvs, omega, gulsize, s):
        
	    # Network and component sizes
	    N=1./ONEoverN
	    N_gullible=N*gulsize
	    N_skeptic=N-N_gullible
        
        
	    # Initial conditions
	    # Gullible
	    pBI0g, pBA0g, pFI0g, pFA0g, pS0g = N_gullible*bi_init, N_gullible*ba_init, 0.0, 0.0, N_gullible*(1.- (ba_init+bi_init))
	    # Skeptical
	    pBI0s, pBA0s, pFI0s, pFA0s, pS0s = N_skeptic*bi_init, N_skeptic*ba_init, 0.0, 0.0, N_skeptic*(1.- (ba_init+bi_init))
        
	    ba=[]
	    fa=[]
	    
	    for i in T:
            
	        # record
	        ba.append(pBA0g+pBA0s)
	        fa.append(pFA0g+pFA0s)
            
	        # update
	        fg  = s*pBA0g/N_gullible+(1-s)*pBA0s/N_skeptic
	        fs = s*pBA0s/N_skeptic+(1-s)*pBA0g/N_gullible
	        
	        pBI1g = alphag * fg * pS0g + omega * pBA0g + (1. - pvg) * (1. - fg) * pBI0g
	        pBA1g = (1. - pvg) * fg * pBI0g + (1. - omega) * (1. - pvg) * pBA0g
	        pFI1g = (1-alphag) * fg * pS0g + omega * pFA0g + pvg * (pBI0g + (1. - omega) * pBA0g) + (1 - fg) * pFI0g
	        pFA1g = fg * pFI0g + (1. - omega) * pFA0g
	        pS1g = (1. - fg) * pS0g
	        
	        pBI1s = alphas * fs * pS0s + omega * pBA0s + (1. - pvs) * (1. - fs) * pBI0s
	        pBA1s = (1. - pvs) * fs * pBI0s + (1. - omega) * (1. - pvs) * pBA0s
	        pFI1s = (1-alphas) * fs * pS0s + omega * pFA0s + pvs * (pBI0s + (1. - omega) * pBA0s) + (1 - fs) * pFI0s
	        pFA1s = fs * pFI0s + (1. - omega) * pFA0s
	        pS1s = (1. - fs) * pS0s
	        
	        pBI0g, pBA0g, pFI0g, pFA0g, pS0g = pBI1g, pBA1g, pFI1g, pFA1g, pS1g
	        pBI0s, pBA0s, pFI0s, pFA0s, pS0s = pBI1s, pBA1s, pFI1s, pFA1s, pS1s
            
	        if float(pBI0s)<=0.0000000001:
	            pBI0s=0.0
	        if float(pBA0s)<=0.0000000001:
	            pBA0s=0.0
	        if float(pFI0s)<=0.0000000001:
	            pFI0s=0.0
	        if float(pFA0s)<=0.0000000001:
	            pFA0s=0.0
	        if float(pS0s)<=0.0000000001:
	            pS0s=0.0
	        if float(pBI0g)<=0.0000000001:
	            pBI0g=0.0
	        if float(pBA0g)<=0.0000000001:
	            pBA0g=0.0
	        if float(pFI0g)<=0.0000000001:
	            pFI0g=0.0
	        if float(pFA0g)<=0.0000000001:
	            pFA0g=0.0
	        if float(pS0g)<=0.0000000001:
	            pS0g=0.0
        
	    return np.cumsum(np.asarray(ba)), np.cumsum(np.asarray(fa))
    
	# To return only one of the types (needed for fitting only against one type)
	def mf_seg_BA(T, alphag, alphas, ONEoverN, ba_init, bi_init, pvg, pvs, omega, gulsize, s):
	    return mf_seg(T, alphag, alphas, ONEoverN, ba_init, bi_init, pvg, pvs, omega, gulsize, s)[0]
    
	def mf_seg_FA(T, alphag, alphas, ONEoverN, ba_init, bi_init, pvg, pvs, omega, gulsize, s):
	    return mf_seg(T, alphag, alphas, ONEoverN, ba_init, bi_init, pvg, pvs, omega, gulsize, s)
    
    
	# Fit functions
	def fit_mf_noseg(T_double, alpha, ONEoverN, ba_init, bi_init, pv, omega):
	    T = T_double[:len(T_double)/2]
	    BA, FA = mf_noseg(T, alpha, ONEoverN, ba_init, bi_init, pv, omega)
	    return np.append(BA, FA)
    
	def fit_mf_seg(T_double, alphag, alphas, ONEoverN, ba_init, bi_init, pvg, pvs, omega, gulsize, s):
	    T = T_double[:len(T_double)/2]
	    BA, FA = mf_seg(T, alphag, alphas, ONEoverN, ba_init, bi_init, pvg, pvs, omega, gulsize, s)
	    return np.append(BA, FA)
    
	# Example
	# import packages
	import numpy as np
	import matplotlib.pyplot as pp
	import pylab
	import scipy
	import pandas as pd
	from scipy.optimize import curve_fit
    
	# Example
	# import packages
	import numpy as np
	import matplotlib.pyplot as pp
	import pylab
	import scipy
	import pandas as pd
	from scipy.optimize import curve_fit
    
    
    
	# Import data
	hoax_data = pd.read_csv(path_file_days+file_name+'.csv',parse_dates=True)
	for_users = hoax_data['For']
	against_users = hoax_data['Against']
	t_empirical=np.arange(0,len(hoax_data))
	len_data= len(hoax_data)
    
	# clean the data a bit - take only the n+1 days
	n=len_data
	t_empirical_month1 = t_empirical[0:n]
	for_users_month1 = for_users[0:n]
	against_users_month1 = against_users[0:n]
    
    
    
	param0 =0.5,0.01,0.1,0.1,0.5,0.5
	param_bounds =([0., 0., 0, 0., 0., 0.], [1., 1., 1., 1., 1., 1.])
    
	# Curve fit
	T_double = np.append(t_empirical_month1, t_empirical_month1)
	data_double = np.append(for_users_month1, against_users_month1)
	popt, cov = curve_fit(fit_mf_noseg, T_double, data_double, p0=param0,bounds=param_bounds, max_nfev=100000)
    
    
    
	# Parameters
	print('alpha = '+ str(round(popt[0], 6)))
	print('network size = ' + str(round(1./popt[1])))
	print('initial BA = ' + str(round(popt[2], 4)))
	print('initial BI = ' + str(round(popt[3], 4)))
	print('pv = ' + str(round(popt[4], 4)))
	print('tau = ' + str(round(1./popt[5], 4)))
    
	# Plot
	BA, FA = mf_noseg(t_empirical_month1,*popt)
	pp.figure()
	pp.plot(t_empirical_month1, for_users_month1, 'b.-',t_empirical_month1,
	        BA,'r+-')
            pp.xlabel("t (days)")
            pp.ylabel("# Active on day t")
            pp.title("Cumilative active believers: data vs. fit")
            pp.legend(['FOR data', 'FOR model'],loc=0)
            pp.savefig(path_figs+file_name+'_fitFORAGAINST2_for.pdf')
            
            pp.figure()
            pp.plot(t_empirical_month1, against_users_month1, 'b.-',t_empirical_month1,
                    FA,'r+-')
                    pp.xlabel("t (days)")
                    pp.ylabel("# Active on day t")
                    pp.title("Cumilative active factcheckers: data vs. fit")
                    pp.legend(['AGAINST data', 'AGAINST model' ],loc=0)
                    pp.savefig(path_figs+file_name+'_fitFORAGAINST2_against.pdf')
                    
                    
                    
                    # Import data
                    hoax_data_hour = pd.read_csv(path_file_hours+file_name+'.csv',parse_dates=True)
                    for_users_hour = hoax_data_hour['For']
                    against_users_hour = hoax_data_hour['Against']
                    t_empirical_hour=np.arange(0,len(hoax_data_hour))
                    len_data_hour= len(hoax_data_hour)
                    
                    # clean the data a bit - take only the n+1 days
                    n=len_data_hour
                    t_empirical_month1_hour = t_empirical_hour[0:n]
                    for_users_month1_hour = for_users_hour[0:n]
                    against_users_month1_hour = against_users_hour[0:n]
                    
                    pp.figure()
                    pp.plot(t_empirical_month1_hour/24.0, for_users_month1_hour, 'g.-',t_empirical_month1,
                            for_users_month1,'g+-')
                            pp.xlabel("t (days)")
                            pp.ylabel("# Active on day t")
                            pp.title("Cumilative active believers: data vs. fit")
                            pp.legend(['FOR data', 'FOR model'],loc=0)
                            pp.savefig(path_figs+file_name+'_fitFORAGAINST2_for.pdf')
                            
                            
                            param0 =0.5,0.0001,0.001,0.001,0.5,0.5
                            param_bounds =([0., 0., 0., 0., 0., 0.], [1., 1., 1., 1., 1., 1.])
                            
                            # Curve fit
                            popt, cov = curve_fit(mf_noseg_BA, t_empirical_month1_hour, for_users_month1_hour, p0=param0,bounds=param_bounds, max_nfev=100000)
                            
                            # Parameters
                            print('alpha = '+ str(round(popt[0], 6)))
                            print('network size = ' + str(round(1./popt[1])))
                            print('initial BA = ' + str(round(popt[2], 4)))
                            print('initial BI = ' + str(round(popt[3], 4)))
                            print('pv = ' + str(round(popt[4], 4)))
                            print('tau = ' + str(round(1./popt[5], 4)))
                            
                            BA, FA = mf_noseg(t_empirical_month1_hour,*popt)
                            pp.figure()
                            pp.plot(t_empirical_month1_hour/24., for_users_month1_hour, 'b.-',t_empirical_month1_hour/24.,
                                    BA,'r+-')
                                    pp.xlabel("t (days)")
                                    pp.ylabel("# Active on day t")
                                    pp.title("Cumilative active believers: data vs. fit")
                                    pp.legend(['FOR data', 'FOR model'],loc=0)
                                    
                                    pp.figure()
                                    pp.plot(t_empirical_month1_hour/24., against_users_month1_hour, 'b.-',t_empirical_month1_hour/24.,
                                            FA,'r+-')
                                            pp.xlabel("t (days)")
                                            pp.ylabel("# Active on day t")
                                            pp.title("Cumilative active factcheckers: data vs. fit")
                                            pp.legend(['AGAINST data', 'AGAINST model' ],loc=0)
                                            
                                            
                                            param0 =0.5,0.0001,0.001,0.001,0.5,0.5
                                            param_bounds =([0., 0., 0., 0., 0., 0.], [1., 1., 1., 1., 1., 1.])
                                            
                                            # Curve fit
                                            popt, cov = curve_fit(mf_noseg_FA, t_empirical_month1_hour, against_users_month1_hour, p0=param0,bounds=param_bounds, max_nfev=100000)
                                            
                                            # Parameters
                                            print('alpha = '+ str(round(popt[0], 6)))
                                            print('network size = ' + str(round(1./popt[1])))
                                            print('initial BA = ' + str(round(popt[2], 4)))
                                            print('initial BI = ' + str(round(popt[3], 4)))
                                            print('pv = ' + str(round(popt[4], 4)))
                                            print('tau = ' + str(round(1./popt[5], 4)))
                                            
                                            BA, FA = mf_noseg(t_empirical_month1_hour,*popt)
                                            pp.figure()
                                            pp.plot(t_empirical_month1_hour/24., for_users_month1_hour, 'b.-',t_empirical_month1_hour/24.,
                                                    BA,'r+-')
                                                    pp.xlabel("t (days)")
                                                    pp.ylabel("# Active on day t")
                                                    pp.title("Cumilative active believers: data vs. fit")
                                                    pp.legend(['FOR data', 'FOR model'],loc=0)
                                                    pp.figure()
                                                    pp.plot(t_empirical_month1_hour/24., against_users_month1_hour, 'b.-',t_empirical_month1_hour/24.,
                                                            FA,'r+-')
                                                            pp.xlabel("t (days)")
                                                            pp.ylabel("# Active on day t")
                                                            pp.title("Cumilative active factcheckers: data vs. fit")
                                                            pp.legend(['AGAINST data', 'AGAINST model' ],loc=0)
                                                            
                                                            param0 =0.5,0.0001,0.001,0.001,0.5,0.5
                                                            param_bounds =([0., 0., 0, 0., 0., 0.], [1., 1., 1., 1., 1., 1.])
                                                            
                                                            # Curve fit
                                                            T_double = np.append(t_empirical_month1_hour, t_empirical_month1_hour)
                                                            data_double = np.append(for_users_month1_hour, against_users_month1_hour)
                                                            popt, cov = curve_fit(fit_mf_noseg, T_double, data_double, p0=param0,bounds=param_bounds, max_nfev=100000)
                                                            
                                                            # Parameters
                                                            print('alpha = '+ str(round(popt[0], 6)))
                                                            print('network size = ' + str(round(1./popt[1])))
                                                            print('initial BA = ' + str(round(popt[2], 4)))
                                                            print('initial BI = ' + str(round(popt[3], 4)))
                                                            print('pv = ' + str(round(popt[4], 4)))
                                                            print('tau = ' + str(round(1./popt[5], 4)))
                                                            
                                                            # Plot
                                                            BA, FA = mf_noseg(t_empirical_month1_hour,*popt)
                                                            pp.figure()
                                                            pp.plot(t_empirical_month1_hour/24., for_users_month1_hour, 'b.-',t_empirical_month1_hour/24., 
                                                                    BA,'r+-')
                                                                    pp.xlabel("t (days)")
                                                                    pp.ylabel("# Active on day t")
                                                                    pp.title("Cumilative active believers: data vs. fit")
                                                                    pp.legend(['FOR data', 'FOR model'],loc=0)
                                                                    pp.savefig(path_figs+file_name+'_non_segregated_BA_hour.pdf')
                                                                    pp.figure()
                                                                    pp.plot(t_empirical_month1_hour/24., against_users_month1_hour, 'b.-',t_empirical_month1_hour/24., 
                                                                            FA,'r+-')
                                                                            pp.xlabel("t (days)")
                                                                            pp.ylabel("# Active on day t")
                                                                            pp.title("Cumilative active factcheckers: data vs. fit")
                                                                            pp.legend(['AGAINST data', 'AGAINST model' ],loc=0)
                                                                            pp.savefig(path_figs+file_name+'_non_segregated_FA_hour.pdf')
                                                                            
                                                                            # Initial parameter estimated
                                                                            # param0 = alphag, alphas, ONEoverN, ba_init, bi_init, pvg, pvs, omega, gulsize, s):
                                                                            param0 =0.5,0.5,0.0001,0.001,0.001,0.5,0.5, 0.5, 0.5, 0.5
                                                                            param_bounds =([0., 0., 0, 0., 0., 0., 0., 0., 0., 0.], [1., 1., 1., 1., 1., 1., 1., 1., 1., 1.])
                                                                            
                                                                            # Curve fit
                                                                            T_double = np.append(t_empirical_month1_hour, t_empirical_month1_hour)
                                                                            data_double = np.append(for_users_month1_hour, against_users_month1_hour)
                                                                            popt, cov = curve_fit(fit_mf_seg, T_double, data_double, p0=param0,bounds=param_bounds, max_nfev=100000)
                                                                            
                                                                            # Parameters
                                                                            print('alphag = '+ str(round(popt[0], 6)))
                                                                            print('alphas = '+ str(round(popt[1], 6)))
                                                                            print('network size = ' + str(round(1./popt[2])))
                                                                            print('initial BA = ' + str(round(popt[3], 4)))
                                                                            print('initial BI = ' + str(round(popt[4], 4)))
                                                                            print('pvg = ' + str(round(popt[5], 8)))
                                                                            print('pvs = ' + str(round(popt[6], 8)))
                                                                            print('tau = ' + str(round(1./popt[7], 4)))
                                                                            print('gullsize = ' + str(round(popt[8], 4)))
                                                                            print('s = ' + str(round(popt[9], 4)))
                                                                            
                                                                            # Plot
                                                                            BA, FA = mf_seg(t_empirical_month1_hour,*popt)
                                                                            pp.figure()
                                                                            pp.plot(t_empirical_month1_hour/24., for_users_month1_hour, 'b.-',t_empirical_month1_hour/24., 
                                                                                    BA,'r+-')
                                                                                    pp.xlabel("t (days)")
                                                                                    pp.ylabel("# Active on day t")
                                                                                    pp.title("Cumilative active believers: data vs. fit")
                                                                                    pp.legend(['FOR data', 'FOR model'],loc=0)
                                                                                    pp.savefig(path_figs+file_name+'_segregated_BA_hour.pdf')
                                                                                    
                                                                                    pp.figure()
                                                                                    pp.plot(t_empirical_month1_hour/24., against_users_month1_hour, 'b.-',t_empirical_month1_hour/24., 
                                                                                            FA,'r+-')
                                                                                            pp.xlabel("t (days)")
                                                                                            pp.ylabel("# Active on day t")
                                                                                            pp.title("Cumilative active factcheckers: data vs. fit")
                                                                                            pp.legend(['AGAINST data', 'AGAINST model' ],loc=0)
	pp.savefig(path_figs+file_name+'_segregated_FA_hour.pdf')
