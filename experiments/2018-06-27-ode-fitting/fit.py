""" Fit an O.D.E. model to empirical data. """

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
import logging
from contextlib import closing

import models

# FIXME: do not use root logger, since it is used by other packages (e.g.
# matplotlib). Create your own logger instance(s).
logger = logging.getLogger()

# Path template
OPATH_LOG = '{model}-{timestamp}.log'
OPATH_MOD = 'models-{model}-{timestamp}.pickle'
OPATH_FIG = 'fig-{model}-{timestamp}-{story:02d}.pdf'

# Used in path template
NOW = datetime.datetime.now().replace(microsecond=0)

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


def readdata(path, stories=None):
    if _ishdf(path):
        # HDFStore where each story is a separate data frame, keyed as
        #
        #   /story_XX
        #
        # Where XX is a two-digit story ID. The dataframes are indexed by
        # timestamp.
        store = pandas.HDFStore(path)
        with closing(store):
            for key in store:
                story = int(re.findall(r"\d+", key)[0])
                if stories is not None and story not in stories:
                    continue
                df = store.get(key)
                df = df.sum(axis=1, level=0)
                yield (story, df)
    elif _iscsv(path):
        # CSV file with all stories, first column is the ID of the story.
        full_df = pandas.read_csv(path, index_col=0, parse_dates=True)
        for story in full_df.index.unique():
            if stories is not None and story not in stories:
                continue
            df = full_df.loc[story].set_index('timestamp')
            yield (story, df)


def fit(df, modelcls='HoaxModel', fity0="non-obs"):
    t0 = df.index[0]
    BA0 = df.loc[t0]['fake']
    FA0 = df.loc[t0]['fact']
    M = getattr(models, modelcls)
    m = M()
    # Initialize model compartments. Fit them or not?
    if fity0 == "all":
        # do nothing -- all y0 will be treated as fit unknowns.
        pass
    elif fity0 == "none":
        # non-observables are set to zero, observables to the data
        m.y0 = numpy.zeros(len(m.y0))
        m.inity0(BA0, FA0)
    elif fity0 == "non-obs":
        # the default: fit non-observables, set observables to the data
        m.inity0(BA0, FA0)
    else:
        raise ValueError("No such option: {}".format(fity0))
    logger.info("Fit y0: {}".format(fity0))
    data = numpy.c_[df['fake'], df['fact']]
    m.fit(data)
    m.summary()
    metrics = {
        "mape": "MAPE",
        "smape": "SMAPE",
        "logaccratio": "LOG ACC. RATIO"
    }
    width = max(map(len, metrics.values()))
    s = "{metric:>{width}}: {err: 6.2f}%"
    for metric in metrics:
        err = m.error(data, metric=metric)
        logger.info(s.format(metric=metrics[metric], width=width, err=err))
    return m


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


def plot(model, df, story):
    t = numpy.arange(len(df))
    fit_data = model.simulate(t)
    fit_df = pandas.DataFrame(fit_data, columns=["fake", "fact"])
    t0 = df.index[0]
    fig, (ax1, ax2) = plt.subplots(1, 2)
    title = r"story {}: $t_0$ = {}".format(story, t0)
    fig.suptitle(title)
    plotone(ax1, df['fake'], fit_df['fake'], "fake")
    plotone(ax2, df['fact'], fit_df['fact'], "fact-check")
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    plt.draw()
    classname = model.__class__.__name__
    output_path = OPATH_FIG.format(story=story, model=classname,
                                   timestamp=NOW.isoformat())
    plt.savefig(output_path)
    logger.info("Written: {}".format(output_path))
    return fig


def mainone(story, df, modelcls='HoaxModel', fity0="non-obs"):
    logger.info("-" * TERM_COLS)
    logger.info("Story: {}".format(story))
    tic = datetime.datetime.now()
    logger.info("Fit started: {}".format(tic))
    fitted_model = fit(df, modelcls=modelcls, fity0=fity0)
    plot(fitted_model, df, story)
    toc = datetime.datetime.now()
    logger.info("Fit ended: {}. Elapsed: {}.".format(toc, toc - tic))
    logger.info("-" * TERM_COLS)
    return fitted_model


def main(path, stories=None, modelcls='HoaxModel', fity0="non-obs", seed=None):
    log_path = OPATH_LOG.format(model=modelcls, timestamp=NOW.isoformat())
    logging.basicConfig(filename=log_path, level=logging.INFO,
                        format='%(asctime)s: %(message)s')
    logging.captureWarnings(True)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    logger.info("Logging to: {}".format(log_path))
    if seed is not None:
        numpy.random.seed(seed)
        logger.info("PRNG Seed: {}".format(seed))
    tic = datetime.datetime.now()
    plt.close("all")
    logger.info("Data: {}".format(path))
    tmp = {
        "seed": seed,
        "fity0": fity0,
        # relative path from user folder. FIXME Define data folder for package.
        "path": os.path.relpath(path, start=os.path.expanduser('~')),
        "modelcls": modelcls,
        "created": NOW.isoformat(),
        "models": {}
    }
    for story, df in readdata(path, stories=stories):
        fitted_model = mainone(story, df, modelcls=modelcls, fity0=fity0)
        tmp["models"][story] = fitted_model
    output_path = OPATH_MOD.format(model=modelcls, timestamp=NOW.isoformat())
    with closing(open(output_path, 'wb')) as f:
        pickle.dump(tmp, f)
        logger.info("Written: {}".format(output_path))
    toc = datetime.datetime.now()
    logger.info("All fits ended. Elapsed (Total): {}.".format(toc - tic))
    if matplotlib.is_interactive():
        plt.show()


epilog = """
By default, all stories in a data file will be fit. If a compartment is not
fit, then it will be initialized as follows. If it is an observable
compartment, it will be set to the first data point of the data; if it is a
non-observable, it be set to zero.
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, epilog=epilog)
    parser.add_argument('path', help="Path to CSV/HDF file with data.")
    parser.add_argument('-s', '--story', type=int, metavar='ID',
                        help='Fit only stories with these %(metavar)s(s)',
                        nargs='+', dest='stories')
    parser.add_argument('-m', '--model', metavar='NAME', default='HoaxModel',
                        help='Fit model %(metavar)s [default: %(default)s]',
                        dest='modelcls', choices=AVAIL_MODELS)
    parser.add_argument('-f', '--fit-y0', default="non-obs", dest='fity0',
                        choices=["all", "none", "non-obs"],
                        help="How to fit the vector of initial conditions "
                        "(default: %(default)s)")
    parser.add_argument('-S', '--seed', type=int, help='PRNG seed')
    args = parser.parse_args()
    main(**vars(args))
