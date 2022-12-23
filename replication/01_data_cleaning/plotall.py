""" Plot fact/fake curve for each story in one single figure. Multiple files
allowed. """

import pandas
import numpy
import matplotlib.pyplot as plt


def plotone(group, key, **kwargs):
    ax = plt.gca()
    group.reset_index(inplace=True)
    group.plot(y='fake', color='gray', ax=ax, legend=False, **kwargs)
    group.plot(y='fact', color='black', ax=ax, legend=False, **kwargs)
    ax.set_title(key, fontsize='small')
    ax.tick_params(labelsize='x-small')
    ax.set_yscale('log')


def plot(df, axs=None, nrows=5, ncols=5, **kwargs):
    """
    Call plotone on each group in data frame on a different axes instance in
    axs array. If axs array is None, create a new subplots figure / axs array
    with given nrows/ncols. Additional keyword arguments are passed to plotone.
    """
    grouped = df.groupby(level=0)
    # create subplots fig/axs
    if axs is None:
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
        plotone(group, key, **kwargs)
    return axs


def main(paths, nrows, ncols):
    fig, axs = plt.subplots(nrows, ncols, sharey=True, sharex=True, figsize=(6, 4))
    for path in paths:
        df = pandas.read_csv(path, index_col=0)
        axs = plot(df, axs)
    plt.tight_layout()
    plt.show()
    return axs


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", help='path to data file(s)', nargs='+')
    parser.add_argument('-r', '--rows', dest='nrows', type=int,
                        help='plot rows (default: %(default)s)',
                        default=5)
    parser.add_argument('-c', '--cols', dest='ncols', type=int,
                        help='plot cols (default: %(default)s)',
                        default=5)
    args = parser.parse_args()
    axs = main(**vars(args))
