import numpy as np
import pandas as pd
from os import listdir
from scipy.optimize import curve_fit
import matplotlib.pyplot as pp
from os.path import isfile, join


# import model and curvefit functions
from mod_func import mf_noseg, mf_seg
from fit_func import fit_mf_noseg, fit_mf_seg


# list of files
path_file ="/Users/marcella/PycharmProjects/hoaxy/data/"
list_of_files=listdir(path_file)


path_output_fig="/Users/marcella/PycharmProjects/untitled/"

# threshold for when a contagion is said to have plateau
# 48, change to higher values if the time span of the hoax is larger
plateau_threshold = 48;
#print(plateau_threshold)

#fit without segregation
for i in range(0,len(list_of_files)):

    # READ DATA
    print(i+1)
    file_name = str(list_of_files[i])
    print(file_name)
    #hoax_data = pd.read_csv(path_file+file_name,parse_dates=True)
    hoax_data=pd.read_csv(path_file+file_name+".csv",parse_dates=True)

    for_users = hoax_data["For"]
    against_users = hoax_data["Against"]
    t_empirical=np.arange(0,len(for_users))

    # FILTER DATA
    # remove the initial plateau from the data
    first_nonzero = np.nonzero(for_users)[0][0]
    for_users = for_users[first_nonzero:]
    against_users = against_users[first_nonzero:]

    # find the position of the end of the dynamics (including buffer plateau at end of length plateau_threshold)
    d_for_users = np.subtract(for_users[plateau_threshold - 1:], for_users[0:-plateau_threshold + 1]);
    d_against_users = np.subtract(against_users[plateau_threshold - 1:], against_users[0:-plateau_threshold + 1]);
    plateau = np.nonzero((np.add(d_for_users, d_against_users)) == 0)[0];
    if (plateau.size > 0):
        temporal_window = plateau[0] + plateau_threshold
        for_users = for_users[0:temporal_window]
        against_users = against_users[0:temporal_window]

    #for_users = for_users[1400:]  #uncomment for 'muslim' and 'sharia', that need a larger temporal window
    #against_users = against_users[1400:] 

    t_empirical = np.arange(0, len(for_users))

    # CURVEFIT AND PLOT WITHOUT SEGREGATION

    param0 = 0.1, 0.0001, 0.001, 0.001, 0.001, 0.001, 0.00001, 0.1
    param_bounds = ([0, 0., 0., 0., 0., 0., 0., 0.], [1., 1., 1., 1., 1., 1., 1., 1.])

    # Curve fit
    T_double = np.append(t_empirical, t_empirical)
    data_double = np.append(for_users, against_users)

    popt, cov = curve_fit(fit_mf_noseg, T_double, data_double, p0=param0, bounds=param_bounds, max_nfev=10000)

    opt_alpha, opt_ONEoverN, opt_ba_init, opt_bi_init, opt_fa_init, opt_fi_init, opt_pv, opt_tau = popt
    opt_alpha_r=round(opt_alpha,6)
    opt_N_r=round(opt_ONEoverN,6)
    opt_ba_r=round(opt_ba_init,6)
    opt_bi_r = round(opt_bi_init, 6)
    opt_fa_r = round(opt_fa_init, 6)
    opt_fi_r = round(opt_fi_init, 6)
    opt_pv_r = round(opt_pv,6)
    opt_tau_r = round(opt_tau,6)

    print("param0:"+str(param0))
    print("alpha opt:"+str(opt_alpha_r))
    print("N opt:" + str(opt_N_r))
    print("init (BA, BI, FA, FI) opt:"+str(opt_ba_r)+", "+str(opt_bi_r)+", "+str(opt_fa_r)+", "+str(opt_fi_r))
    print("verify opt:"+str(opt_pv_r))
    print(opt_pv)
    print("tau opt"+str(opt_tau_r))


    BA, FA = mf_noseg(t_empirical, *popt)
    print(max(FA))

    pp.figure()
    pp.plot(t_empirical / 24., BA, 'b-',t_empirical / 24., FA, 'r-')
    pp.xlabel("t (days)")
    pp.ylabel("# Active on day t")
    pp.title(file_name + "NO_SEG")
    pp.legend(['FOR model', 'AGAINST model'], loc=7)
    pp.savefig(path_output_fig + "-" + file_name + "_noseg.pdf")

    pp.figure()
    pp.plot(t_empirical / 24., for_users, 'b+',
            t_empirical / 24., BA, 'b-',
            t_empirical / 24., against_users, 'r+',
            t_empirical / 24., FA, 'r-')
    pp.xlabel("t (days)")
    pp.ylabel("# Active on day t")
    pp.title(file_name + "NO_SEG")
    pp.legend(['FOR data', 'FOR model', 'AGAINST data', 'AGAINST model'], loc=7)
    pp.savefig(path_output_fig +str(i) + "-" + file_name + "_noseg.pdf")
    #pp.show()


    np.savetxt(file_name + '_without_segregation_param.out', popt)
    np.savetxt(file_name + '_without_segregation_cov.out', cov)
    np.savetxt(file_name + '_without_segregation.out', (t_empirical / 24., for_users, BA, against_users, FA))
    print('END - FIT without seg')

    # CURVEFIT AND PLOT WITH SEGREGATION
    # params = [T, alpha, ONEoverN, ba_init, bi_init, fa_init, fi_init, pvg, pvs, tau, gulsize, seg]

    param2_0 = 0.1, 0.0001, 0.001, 0.001, 0.001, 0.001, 0.05, 0.00, 0.0001, 0.5, 0.5
    param2_bounds = ([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.5],
                    [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.])

    # Curve fit
    T_double2 = np.append(t_empirical, t_empirical)
    data_double2 = np.append(for_users, against_users)

    popt2, cov2 = curve_fit(fit_mf_seg, T_double2, data_double2, p0=param2_0, bounds=param2_bounds, max_nfev=10000)

    opt_alpha, opt_ONEoverN, opt_ba_init, opt_bi_init, opt_fa_init, opt_fi_init, opt_pvg, opt_pvs, opt_tau, opt_gulsize, opt_seg = popt2

    opt_alpha_r = round(opt_alpha, 6)
    opt_N_r = round(opt_ONEoverN, 6)
    opt_ba_r = round(opt_ba_init, 6)
    opt_bi_r = round(opt_bi_init, 6)
    opt_fa_r = round(opt_fa_init, 6)
    opt_fi_r = round(opt_fi_init, 6)
    opt_pvg_r = round(opt_pvg, 6)
    opt_pvs_r = round(opt_pvs, 6)
    opt_tau_r = round(opt_tau, 6)
    opt_seg_r = round(opt_seg, 6)
    opt_gsize_r = round(opt_gulsize, 6)

    print("param2_0:" + str(param2_0))
    print("alpha opt:" + str(opt_alpha_r))
    print("N opt:" + str(opt_N_r))
    print("init (BA, BI, FA, FI) opt:" + str(opt_ba_r) +", "+ str(opt_bi_r) +", "+ str(opt_fa_r) +", "+ str(opt_fi_r))
    print("verify opt gul :" + str(opt_pvg_r))
    print("verify opt skep:" + str(opt_pvs_r))
    print("tau opt" + str(opt_tau_r))
    print("seg opt" + str(opt_seg_r))
    print("gsize opt" + str(opt_gsize_r))


    # Plot
    BA2, FA2 = mf_seg(t_empirical, *popt2)
    print(max(FA2))
    pp.figure()
    pp.plot(t_empirical / 24., for_users, 'b+',
            t_empirical / 24., BA2, 'b-',
            t_empirical / 24., against_users, 'r+',
            t_empirical / 24., FA2, 'r-')
    pp.xlabel("t (days)")
    pp.ylabel("# Active on day t")
    pp.title(file_name + "SEG")
    pp.legend(['FOR data', 'FOR model', 'AGAINST data', 'AGAINST model'], loc=7)
    pp.savefig(path_output_fig + str(i) + "-" + file_name + "_seg.pdf")
    #pp.show()

    np.savetxt(path_output_fig + file_name + '_with_segregation_param.out', popt2)
    np.savetxt(path_output_fig + file_name + '_with_segregation_cov.out', cov2)
    np.savetxt(path_output_fig + file_name + '_with_segregation.out', (t_empirical / 24., for_users, BA2, against_users, FA2))

    print('END - FIT with seg')
