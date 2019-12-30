""" Fit an O.D.E. model to one or more stories. """

from __future__ import print_function
import os
import sys
import re
import pickle
import datetime
import numpy
import pandas
import matplotlib
import matplotlib.pyplot as plt
import argparse
from contextlib import closing

import models

# Path template
OPATH = 'story{storyid:02d}-{model}-{date}T{hour}.{format}'

# Used in path template
NOW = datetime.datetime.now()

# Used by cmd line parser
AVAIL_MODELS = [v.__name__ for v in models.__dict__.values()
                if isinstance(v, type) and issubclass(v, models.ODEModel)]
# The base class -- cannot be chosen
AVAIL_MODELS.remove('ODEModel')

# Find out terminal size
py_vers = sys.version_info
if py_vers.major >= 3 and py_vers.minor >= 3:
    import shutil
    # on Python 3.3+ use os.get_terminal_size
    TERM_COLS = shutil.get_terminal_size().columns
elif os.name is "posix":
    # if that's not available ...
    # ... on Linux/Unix use stty to get terminal size
    import subprocess
    result = subprocess.getoutput("stty size")
    _, TERM_COLS = map(int, result.split())
else:
    # ... on Windows assume default of 80 columns
    TERM_COLS = 80


def _iscsv(path):
    pat = r".*\.csv.*"
    m = re.match(pat, path, flags=re.IGNORECASE)
    return m is not None


def _ishdf(path):
    pat = r".*\.h(df|5).*"
    m = re.match(pat, path, flags=re.IGNORECASE)
    return m is not None


def readdata(path, storyid):
    if _ishdf(path):
        store = pandas.HDFStore(path)
        with closing(store):
            k = "/story_{:02d}".format(storyid)
            df = store.get(k)
    elif _iscsv(path):
        df = pandas.read_csv(path, index_col=0, parse_dates=True)
        df = df.loc[storyid].set_index('timestamp')
    if df.columns.nlevels > 1:
        # Aggregate multiple URLs
        df = df.sum(axis=1, level=0)
    return df


def fit(df, modelcls='HoaxModel'):
    t0 = df.index[0]
    M = getattr(models, modelcls)
    m = M()
    BA0 = df.loc[t0]['fake']
    FA0 = df.loc[t0]['fact']
    try:
        m.inity0(BA0, FA0)
    except NotImplementedError:
        pass
    data = numpy.c_[df['fake'], df['fact']]
    m.fit(data)
    m.summary()
    metrics = {
        "mape": "MAPE",
        "smape": "SMAPE",
        "logaccratio": "LOG ACC. RATIO"
    }
    width = max(map(len, metrics.values()))
    for metric in metrics:
        err = m.error(data, metric=metric)
        print("{metric:>{width}}: {err: 6.2f}%".format(metric=metrics[metric],
                                                       width=width,
                                                       err=err))
    t = numpy.arange(len(df))
    fit_data = m.simulate(t)
    fit_df = pandas.DataFrame(fit_data, columns=["fake", "fact"])
    return fit_df, m


def plotone(ax, data_df, fit_df, title):
    data_df.plot(color='k', ls='', marker='o', ax=ax)
    fit_df.plot(color='r', ls='-', ax=ax)
    ax.legend(["Data", "Fit"], loc='best')
    ax.set_title(title)
    ax.set_yscale('symlog')
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin, ymax * 10)
    ax.set_xlabel('Hours since $t_0$')
    ax.set_ylabel('Active Users')
    return ax.lines


def plot(story_df, fit_df, storyid, modelcls='HoaxModel', save_fig=False):
    t0 = story_df.index[0]
    fig, (ax1, ax2) = plt.subplots(1, 2)
    title = r"story {}: $t_0$ = {}".format(storyid, t0)
    fig.suptitle(title)
    plotone(ax1, story_df['fake'], fit_df['fake'], "fake")
    plotone(ax2, story_df['fact'], fit_df['fact'], "fact-check")
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    plt.draw()
    if save_fig:
        output_path = OPATH.format(storyid=storyid, model=modelcls,
                                   date=NOW.date(), hour=NOW.time(),
                                   format='pdf')
        plt.savefig(output_path)
        print("Written: {}".format(output_path))
    return fig


def mainone(path, storyid, modelcls='HoaxModel', save_fig=False,
            save_model=False):
    print("-" * TERM_COLS)
    print("Story: {}".format(storyid))
    tic = datetime.datetime.now()
    print("Fit started: {}".format(tic))
    story_df = readdata(path, storyid)
    fit_df, model = fit(story_df, modelcls=modelcls)
    if save_model:
        output_path = OPATH.format(storyid=storyid, model=modelcls,
                                   date=NOW.date(), hour=NOW.time(),
                                   format='pickle')
        with closing(open(output_path, 'wb')) as f:
            pickle.dump(model, f)
            print("Written: {}".format(output_path))
    story_df.reset_index(inplace=True)
    plot(story_df, fit_df, storyid, modelcls=modelcls, save_fig=save_fig)
    toc = datetime.datetime.now()
    print("Fit ended: {}. Elapsed: {}.".format(toc, toc - tic))
    print("-" * TERM_COLS)
    print()
    return toc - tic


def main(path, storyid, modelcls='HoaxModel', save_fig=False,
         save_model=False):
    print("Data: {}".format(path))
    elapsed = datetime.timedelta(0)
    plt.close("all")
    for _storyid in storyid:
        elapsed += mainone(path, _storyid, save_fig=save_fig,
                           save_model=save_model, modelcls=modelcls)
    print("Elapsed (Total): {}.".format(elapsed))
    if matplotlib.is_interactive():
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', help="Path to HDF file with data")
    parser.add_argument('storyid', type=int, help='ID of story to plot',
                        nargs='+')
    parser.add_argument('-m', '--model', metavar='NAME', default='HoaxModel',
                        help='Fit model %(metavar)s [default: %(default)s]',
                        dest='modelcls', choices=AVAIL_MODELS)
    parser.add_argument('-F', '--save-fig', action='store_true',
                        help='save figure(s) to PDF')
    parser.add_argument('-M', '--save-model', action='store_true',
                        help='save model(s) to pickle')
    args = parser.parse_args()
    main(**vars(args))
