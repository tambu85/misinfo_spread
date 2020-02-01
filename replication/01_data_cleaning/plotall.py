""" Plot fact/fake curve for each story in one single figure """

import pandas
import numpy
import matplotlib.pyplot as plt


def plotone(group, key):
    ax = plt.gca()
    group.reset_index(inplace=True)
    group.plot(y='fake', ax=ax, legend=False)
    group.plot(y='fact', ax=ax, legend=False)
    ax.set_title(key, fontsize='small')


def plot(path, nrows=5, ncols=5):
    df = pandas.read_csv('data_tweets.csv')
    grouped = df.groupby('story_id')
    fig, axs = plt.subplots(nrows, ncols, sharex=True)

    # Check nrows and ncols OK
    N_plots = nrows * ncols
    N_groups = len(grouped.groups)
    if N_groups > N_plots:
        import sys
        print("Not enough rows/cols: {}; need {}.".format(N_plots, N_groups),
              file=sys.stderr)
        sys.exit(1)

    for i, (key, group) in enumerate(grouped):
        h, k = numpy.unravel_index(i, axs.shape)
        plt.sca(axs[h, k])
        plotone(group, key)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help='path to data file')
    parser.add_argument('-r', '--rows', dest='nrows', type=int,
                        help='plot rows (default: %(default)s)',
                        default=5)
    parser.add_argument('-c', '--cols', dest='ncols', type=int,
                        help='plot cols (default: %(default)s)',
                        default=5)
    args = parser.parse_args()
    plot(**vars(args))
