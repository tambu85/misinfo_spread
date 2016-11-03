#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import pylab
import scipy
import pandas as pd
from scipy.optimize import curve_fit
from  models_functions import mf_seg, mf_noseg, sir, mf_seg_plot, mf_noseg_plot


hoax_data = pd.read_csv('hoaxy_dr-drew-hillary-clinton-health_cum.csv',parse_dates=True)
for_users = hoax_data['For']
against_users = hoax_data['Against']
t_empirical=np.arange(0,len(hoax_data))
len_data= len(hoax_data)

#DATA FITTING
#mf_seg
param0=[0.15,0.1, 5500, 0.5, 0.05, 0.2, 0.5, 10]
param_bounds =([0.001,0, 1, 0.1, 0, 0, 0.5, 5], [10.,1., 2000000, 0.9, 0.9, 0.2, 1., 15])

popt, pcov = scipy.optimize.curve_fit(mf_seg,
                                          t_empirical,
                                          for_users,
                                          p0=param0,
                                          bounds=param_bounds)

[tfact,alpha, net_size, gullible_size, bainit, pvsk, segregation, tau] = popt
print('MF WITH SEGREGATION')
print(pcov)
print('tfact='+str(tfact))
print('alpha = '+ str(round(alpha, 2)))
print('network size = ' + str(round(net_size)))
print('gullible size= ' + str(round(gullible_size, 2)))
print(' initial BA = ' + str(round(bainit, 2)))
print('verify SK = ' + str(round(pvsk, 2)))
print('segregation = ' + str(round(segregation, 2)))
print('tau = ' + str(round(tau)))
print('*****************')


# plot fit and data
t_plot = np.arange(0, len_data+tfact, tfact)

for j in range(0, len(t_plot)):
    t_plot[j] = round(t_plot[j], 5)

t_plot= np.unique(np.sort(np.append(t_plot, t_empirical)))
ba_plot=mf_seg_plot(t_plot, alpha, net_size, gullible_size, bainit, pvsk, segregation, tau)

pylab.figure()
pylab.axis([0.0,max(t_empirical), 0, max(for_users)+200])
#pylab.axis([0.0,max(t_empirical), 0, max(ba_plot)])
ax = pylab.gca()
ax.set_autoscale_on(False)
pylab.plot(t_empirical, for_users, '.', label='data point')
pylab.plot(t_plot,ba_plot , label='fit_seg')

#print(abs(ba - for_users))

#mf_noseg
param0=[0.05,0.05, 2550, 0.05, 0, 10]
param_bounds =([0.001,0, 1000, 0, 0,  5], [10,1., 2000000, 0.3, 0.05, 15])
#t_sim = scipy.linspace(0, len(hoax_data), 180)
popt, pcov = scipy.optimize.curve_fit(mf_noseg,
                                        t_empirical,
                                        for_users,
                                        p0=param0,
                                        bounds=param_bounds)

[tfact, alpha, net_size,  bainit, pv, tau] = popt
print('MF WITHOUT SEGREGATION')
print(pcov)
print('tfact=' + str(tfact))
print('alpha = ' + str(round(alpha, 2)))
print('network size = ' + str(round(net_size)))
print(' initial BA = ' + str(round(bainit, 2)))
print('verify = ' + str(round(pv, 2)))
print('tau = ' + str(round(tau)))
#

# plot fit and data

t_plot = np.arange(0, len_data+tfact, tfact)
for j in range(0, len(t_plot)):
    t_plot[j] = round(t_plot[j], 5)

t_plot= np.unique(np.sort(np.append(t_plot, t_empirical)))
ba_plot= mf_noseg_plot(t_plot, alpha, net_size, bainit, pv, tau)
pylab.plot(t_plot, ba_plot, label='fit_noseg')

#sir
param0=[0.2, 0.8, 0., 2300]
param_bounds =([0, 0, 0, 1000], [1., 1., 1.,  2000000])

popt, pcov = scipy.optimize.curve_fit(sir, t_empirical,
                                           for_users,
                                           p0=param0,
                                           bounds=param_bounds)

[bainit, beta,  mu, net_size] = popt
print('SIR')
print(pcov)
print('beta = ' + str(round(beta, 2)))
print('network size = ' + str(round(net_size)))
print(' initial BA = ' + str(round(bainit, 2)))
print('mu = ' + str(round(mu, 2)))
#
infected=sir(t_empirical,  bainit, beta, mu, net_size)
pylab.plot(t_empirical, infected, label='sir')

pylab.title('FIT PARAMETERS')
pylab.legend()
pylab.legend(['For Users', 'Model with segregation', 'Model without segregation',"SIR"],
             loc='lower right'
             )

#pylab.legend(['For Users', 'Model with segregation', 'Model without segregation', "SIR"])
pylab.savefig('hoaxy_drdrew_tryfit_cum.pdf', format='pdf')





