""" Produce scatter plot of fake vs fact """

import numpy
import scipy.stats
import math
import argparse
import pandas
import matplotlib.pyplot as plt

def getsize(size):
    s = math.sqrt(size)
    nrows = math.ceil(s)
    ncols = math.ceil(size / nrows)
    assert nrows * ncols >= size
    return (nrows, ncols)

def f(group):
    group['fake'] = group['fake'].cumsum()
    group['fact'] = group['fact'].cumsum()
    return group

def make_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", help="Path to CSV file with data")
    parser.add_argument("-f", "--figure", help="Path to output PDF figure")
    parser.add_argument("-c", "--cumulative", action="store_true", 
                        help="Plot cumulative data")
    parser.add_argument("-s", "--stories", help="Path to text file "
                        "list of stories to plot (one per line)")
    parser.add_argument("-x", "--sharexy", action="store_true",
                        help="Share X and Y axes across subplots")
    parser.add_argument("-z", "--zero", action="store_true",
                        help="Axes start at zero (one in loglog scale)")
    parser.add_argument("-l", "--loglog", action="store_true",
                        help="Use loglog scale instead of linear")
    parser.add_argument("-r", "--regress", action="store_true",
                        help="Plot robust linear fit")
    return parser

def main(args):
    df = pandas.read_csv(args.data)
    if args.stories is not None:
        _df = pandas.read_csv(args.stories, names=["stories"])
        stories = list(_df['stories'])
    else:
        stories = list(df['story_id'].unique())
    nrows, ncols = getsize(len(stories))
    if args.cumulative:
        df = df.groupby('story_id', as_index=False).apply(f)
    grouped = df.groupby('story_id')
    fig, axs = plt.subplots(nrows=nrows,
                            ncols=ncols, 
                            figsize=(1.5 * ncols, 1.25 * nrows), 
                            sharex=args.sharexy, 
                            sharey=args.sharexy)
    for (key, ax) in zip(stories, axs.flatten()):
        g = grouped.get_group(key).query('fake > 0 & fact > 0')
        g.plot(ax=ax, kind='scatter', x='fake', y='fact', 
               loglog=args.loglog, color='gray', marker='.') 
        if args.regress:
            res = scipy.stats.siegelslopes(g['fact'], g['fake'])
            x = numpy.linspace(g['fake'].min(), g['fake'].max())
            y = res[0] * x + res[1]
            ax.plot(x, y, "--", color="black")
        ax.set_title(key)
    if args.zero:
        if args.sharexy:
            for ax in axs.flatten():
                ax.set_xlim(1 if args.loglog else 0, ax.get_xlim()[1])
                ax.set_ylim(0.8 if args.loglog else 0, ax.get_ylim()[1])
        else:
            xlim_upper = max(ax.get_xlim()[1] for ax in axs.flatten())
            ylim_upper = max(ax.get_ylim()[1] for ax in axs.flatten())
            ax.set_xlim(1 if args.loglog else 0, xlim_upper)
            ax.set_ylim(0.8 if args.loglog else 0, ylim_upper)
    plt.tight_layout()
    if args.figure is not None:
        plt.savefig(args.figure)
        print("Written: {}".format(args.figure))
    plt.show()

if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    main(args)
