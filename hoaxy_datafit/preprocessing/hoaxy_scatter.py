

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pylab
import pandas as pd

topic=["hoaxy_three-syrian-refugees-assault-5-year-old-girl-at-knifepoint",
       "hoaxy_black-protesters-targeted-whites-in-milwaukee",
       "hoaxy_mexico-border-trump-elected",
       "hoaxy_julian-assange-bernie-sanders-was-threatened",
       "hoaxy_deray-mckesson-and-the-summer-of-chaos"]

for i in range(len(topic)):
    filename = topic[i] + ".csv"
    clean_data = pd.read_csv(filename, parse_dates=True)
    time_intervals = clean_data['Date']
    time = range(len(time_intervals))
    for_list = clean_data['For']+np.ones(len(clean_data))
    against_list = clean_data['Against']+np.ones(len(clean_data))

    pylab.figure()
    ax = pylab.gca()
    ax.set_xscale('log')
    ax.set_yscale('log')
    pylab.xlabel('fake')
    pylab.ylabel('debunking')
    pylab.plot(for_list,against_list, 'o', color='blue')
    pylab.title(topic[i])
    pylab.savefig('hoaxy_scatter_plot_LOG_' + topic[i] + '.pdf', format='pdf')


