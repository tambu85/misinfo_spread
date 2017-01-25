#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

topic=["hoaxy_three-syrian-refugees-assault-5-year-old-girl-at-knifepoint",
       "hoaxy_black-protesters-targeted-whites-in-milwaukee",
       "hoaxy_mexico-border-trump-elected",
       "hoaxy_julian-assange-bernie-sanders-was-threatened",
       "hoaxy_deray-mckesson-and-the-summer-of-chaos",
       "hoaxy_three-syrian-refugees-assault-5-year-old-girl-at-knifepoint_cum",
       "hoaxy_black-protesters-targeted-whites-in-milwaukee_cum",
       "hoaxy_mexico-border-trump-elected_cum",
       "hoaxy_julian-assange-bernie-sanders-was-threatened_cum",
       "hoaxy_deray-mckesson-and-the-summer-of-chaos_cum"
       ]

for i in range(len(topic)):
    filename = topic[i] + ".csv"
    clean_data = pd.read_csv(filename, parse_dates=True)
    dates = clean_data['Date']
    for_list = clean_data['For']
    against_list = clean_data['Against']

    x = [datetime.strptime(d, '%Y-%m-%d').date() for d in dates]

    plt.figure()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.plot(x, for_list, label='for', color='blue')
    plt.plot(x, against_list, label='against', color='red')
    plt.gcf().autofmt_xdate()
    ax = plt.gca()
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    myLocator = mticker.MultipleLocator(len(clean_data)/15)
    ax.xaxis.set_major_locator(myLocator)
    plt.ylim(-30, max(max(for_list),max(against_list))+200)
    plt.title(topic[i])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig('hoaxy_plot_' + topic[i] + '.pdf', format='pdf')



