from __future__ import print_function

import json
import pandas
import numpy
from contextlib import closing
from plotting import plotall, plotonewithurls
from fitting import fitone, fitmany, gendata
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

print(len(data))
#print(data[3])

# This will aggregate all the `fake' and `fact' column groups, and will
# concatenate all the data frames in one single data frame. These are the data
# that can be used for the fit.
df = pandas.concat(dict((k, df.sum(axis=1, level=0))
                        for k, df in data.items()), names=['story_id'])

# This data frame is indexed by the ID of each story. So to get story with ID 7
# (see spreadsheet) you just use the dataframe

print(df.loc[7].index[0])


# ADDITIONAL:
# these are the URLs of each story, useful for figure titles or legends
with closing(open(urls_json_path)) as f:
    urls = json.load(f)

k=sorted(data.keys())
#print(k)
k0=k[0]
#print(urls[str(k0)]['fact'])



if __name__ == '__main__':

    import models
    N_max = 1e6

    # All initial conditions are unknown parameters to fit
    bounds = [
            (0, N_max),  # BA
            (0, N_max),  # FA
            (0, N_max),  # BI
            (0, N_max),  # FI
            (0, N_max),  # S
            (0, 1),  # pv
            (0, 1),  # tauinv
            (0, 1),  # alpha
        ]



    chosenid=7
    mystory = df.loc[chosenid]
    t0 = mystory.index[0]
    t = numpy.linspace(0, len(mystory) - 1, len(mystory))
    data7 = numpy.c_[t, mystory.values]
    #print(data7)

    xopt, err = fitone(data7, models.hoaxmodel, 5, bounds, fity0=True, nrep=1)
    numpy.set_printoptions(precision=2, suppress=True)
    print("{} +/- {}".format(numpy.round(xopt, 2), numpy.round(err, 2)))

    [ba_opt, fa_opt, bi_opt, fi_opt, s_opt, pv_opt, tauinv_opt, alpha_opt]=numpy.round(xopt,2)
    y0 = (ba_opt, fa_opt, bi_opt, fi_opt, s_opt)
    sigma=0
    fit_data = gendata(models.hoaxmodel, y0, t, sigma, pv_opt, tauinv_opt, alpha_opt)
    fit_data = fit_data[:,1:3]
    fit_df = pandas.DataFrame.from_records(fit_data)
    fit_df.columns=["ba_fit","fa_fit"]
    fit_df.index=mystory.index

    print(fit_df.head())

    k=7
    fig, (ax1, ax2) = plt.subplots(1, 2)
    title = "FITTING Story " + str(k) + ": $t_0=$ {}".format(t0)
    fig.suptitle(title)


    ax1 = plt.subplot(1, 2, 1)
    mystory['fake'].plot(legend=True, color='k', ls='--', ax=ax1, title="Fake-data")
    fit_df['ba_fit'].plot(legend=True, color='k', ls='-',ax=ax1, title="Fake-fit")
    ax1.set_yscale('symlog')
    ymin, ymax = ax1.get_ylim()
    ax1.set_ylim(ymin, ymax * 10)
    ax1.set_xlabel('Hours since $t_0$')
    ax1.set_ylabel('Active Users')


    ax2 = plt.subplot(1, 2, 2)
    mystory['fact'].plot(legend=True, color='r', ls='--', ax=ax2, title="Factcheck-data")
    fit_df['fa_fit'].plot(legend=True, color='r',ls='-', ax=ax2, title="Factcheck-fit")
    ax2.set_yscale('symlog')
    ymin, ymax = ax2.get_ylim()
    ax2.set_ylim(ymin, ymax * 10)
    ax2.set_xlabel('Hours since $t_0$')


    plt.subplots_adjust(top=0.88)
    plt.tight_layout()

    plt.show()