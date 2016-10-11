#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd

topic = ["hoaxy_three-syrian-refugees-assault-5-year-old-girl-at-knifepoint",
         "hoaxy_black-protesters-targeted-whites-in-milwaukee",
         "hoaxy_mexico-border-trump-elected",
         "hoaxy_julian-assange-bernie-sanders-was-threatened",
         "hoaxy_deray-mckesson-and-the-summer-of-chaos"
         ]


for j in range(len(topic)):

    filename = topic[j] + ".csv"

    # open the csv of non cumulative data
    df = pd.read_csv(filename, parse_dates=True)

    #compute the cumulative occurences
    for i in range(1, len(df)):
        df.loc[i] = [df['Date'][i], df['For'][i-1]+df['For'][i], df['Against'][i-1]+df['Against'][i]]

    filename=topic[j]+'_cum.csv'
    #write the cumulative dataframe in a new csv file
    df.to_csv(filename, index=False)

