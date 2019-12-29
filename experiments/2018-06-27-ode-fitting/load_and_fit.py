from __future__ import print_function

import datetime
import numpy
import pandas
import matplotlib
import matplotlib.pyplot as plt
import argparse
from contextlib import closing

import models


def readdata(path, storyid):
    store = pandas.HDFStore(path)
    with closing(store):
        try:
            df = store.get("/story_{:02d}".format(storyid))
        except KeyError:
            import sys
            print("No such story: {}".format(storyid), file=sys.stderr)
            sys.exit(-1)
        df = df.sum(axis=1, level=0)
        return df


def plotfit(ax, data_df, fit_df, title):
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


def main(path, storyid, output=None):
    story_df = readdata(path, storyid)
    t0 = story_df.index[0]

    m = models.HoaxModel()
    m.FA = story_df.loc[t0]['fact']
    m.BA = story_df.loc[t0]['fake']
    data = numpy.c_[story_df['fake'], story_df['fact']]
    m.fit(data)
    xopt = numpy.hstack([m.y0, m.theta])
    names = m._y0 + m._theta
    err = m.err_
    for n, x, e in zip(names, xopt, err):
        print("{}: {:.2e} +/- {:.2e}".format(n, x, e))

    t = numpy.arange(len(story_df))
    fit_data = m.simulate(t)
    fit_df = pandas.DataFrame(fit_data, columns=["fake", "fact"])
    story_df.reset_index(inplace=True)

    toc = datetime.datetime.now()
    print("Ended: {}".format(toc))
    print("Elapsed: {}".format(toc - tic))

    fig, (ax1, ax2) = plt.subplots(1, 2)
    title = r"story {}: $t_0$ = {}".format(storyid, t0)
    fig.suptitle(title)

    plotfit(ax1, story_df['fake'], fit_df['fake'], "fake")
    plotfit(ax2, story_df['fact'], fit_df['fact'], "fact-check")

    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    plt.draw()
    if output is not None:
        plt.savefig(output)
    if matplotlib.is_interactive():
        plt.show()


if __name__ == '__main__':
    tic = datetime.datetime.now()
    print("Started: {}".format(tic))

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path')
    parser.add_argument('storyid', type=int, help='ID of story to plot')
    parser.add_argument('-o', '--output', metavar='FILE',
                        help='save figure to %(metavar)s')
    args = parser.parse_args()
    main(args.path, args.storyid, args.output)
