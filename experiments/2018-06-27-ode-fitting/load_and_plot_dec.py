from __future__ import print_function

import json
import pandas
from contextlib import closing
from plotting import plotall, plotonewithurls
import models
import matplotlib.pyplot as plt

# place the data files in the `data' folder in the root of the repository
# folder
hdf_store_path = '../../data/data.hdf'
urls_json_path = '../../data/data.json'

store = pandas.HDFStore(hdf_store_path)

# this reads the data into a dictionary of data frames. The columns of these
# data frames are organized in two groups of columns, the `fake' and `fact'
# groups. For each group, the data are disaggregated by individual URLs. So for
# example if a story was published in 2 fake news articles and 3 fact-checking
# articles the data frame will have two groups of columns, the first with 2
# columns and the second with 3, for a total of 5 columns.
with closing(store):
    data = dict((int(k.split('_')[1]), store[k]) for k in store)

for k in data:
    data[k] = data[k].diff()

# This will aggregate all the `fake' and `fact' column groups, and will
# concatenate all the data frames in one single data frame. These are the data
# that can be used for the fit.
df = pandas.concat(dict((k, df.sum(axis=1, level=0))
                        for k, df in data.items()), names=['story_id'])

# This data frame is indexed by the ID of each story. So to get story with ID 7
# (see spreadsheet) you just use the dataframe

print(df.head())
#print(df['fact'])


# ADDITIONAL:
# these are the URLs of each story, useful for figure titles or legends
with closing(open(urls_json_path)) as f:
    urls = json.load(f)

k=sorted(data.keys())
#print(k)
#k0=k[0]
#print(urls[str(k0)]['fact'])

plotall(df, 4, 4, (8,8))
storyid=0
print("Do you want to plot a single story (insert the story id or 0)?")
storyid=int(input())
while storyid > 0:
    print("Plot story " + str(storyid))
    plotonewithurls(data[storyid],storyid)
    print("Do you want to plot a single story (insert the story id or 0)?")
    storyid = int(input())



