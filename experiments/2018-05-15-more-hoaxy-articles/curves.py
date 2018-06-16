#!/usr/bin/env python

""" Create curves for data fitting. Requires Pandas 0.18+ for new resampling
interface. """

from __future__ import print_function

import os
import sys
import argparse
import pandas
import math
import numpy
import json
from itertools import count
from collections import defaultdict

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('input', help='CSV input file')
parser.add_argument('output', help='HDF store output')
parser.add_argument('-f', '--freq', default='H',
                    help='Sampling frequency (default: %(default)s)')
parser.add_argument('-F', '--force-overwrite', action='store_true',
                    help='Force overwrite of output file')
parser.add_argument('--min-tweets-each', type=int, default=100,
                    help='Filter story with at least %(metavar)s '
                    'tweets each type (default: %(default)d)', metavar='NUM')
parser.add_argument('--min-tweets-total', type=int, default=1000,
                    help='Filter story with at least %(metavar)s '
                    'tweets (default: %(default)d)', metavar='NUM')
parser.add_argument('--keep-plateau', action='store_false', dest='trim',
                    help='Do not remove trailing plateau (default: False)')
parser.add_argument('--min-degree', type=float, default=1.0,
                    dest='mindeg', help='Plateau found growth angle'
                    'below %(metavar)s (default: %(default).1f deg)',
                    metavar='DEG')


def filterstories(df, min_tweets_total=1000, min_tweets_each=100):
    """
    Filter stories from original data to have only

    1. At least a certain number of tweets for each story
    2. Both `fact` and `fake` types have tweets
    3. The `fact` curve lags the `fake` curve, not viceversa

    Finally, reassign story_id to remove gaps.
    """
    df = df.groupby('story_id').filter(lambda k: len(k) >= min_tweets_total)

    n_tweets = df.groupby(['story_id', 'tweet_type']).count()['tweet_id']
    n_tweets = n_tweets.unstack().fillna(0)
    idx = (n_tweets['fact'] > min_tweets_each) & \
        (n_tweets['fake'] > min_tweets_each)
    df = df.set_index('story_id').loc[idx].reset_index()

    tmin_df = df.groupby(['story_id', 'tweet_type']).agg({'created_at': 'min'})
    tmin_df = tmin_df.unstack()['created_at']
    idx = tmin_df['fact'] > tmin_df['fake']
    df = df.set_index('story_id').loc[idx].reset_index()

    # sort and reindex to remove gaps
    df = df.set_index('story_id').sort_index().reset_index()
    story_id_values = df['story_id'].unique()
    mapper = dict(zip(story_id_values, range(len(story_id_values))))
    df['story_id'] = df['story_id'].map(mapper.__getitem__)
    return df


def _activeusers(df, freq='H'):
    """
    This function is used to create the time series of active users for
    each individual URL.

    Do not use this function directly. Instead, see the docstring of
    `timeseries`.
    """
    key = ['tweet_type', 'clean_url']
    df = df.set_index('created_at')
    df = df.groupby(key).resample(freq).agg({'user_id': 'nunique'})
    df = df.rename(columns={'user_id': 'active_users'})
    df.index.rename('timestamp', level=-1, inplace=True)
    return df.cumsum()


def _findplateau(y, x=None, mindeg=1.0):
    """
    Find the value at which a curve reaches its plateau. A plateau is
    reached when the angle tangent to the curve at any given point is
    below a small threshold (default, 1 degree).

    Parameters
    ==========
    y : ndarray
        An array of monotonically increasing values

    x : ndarray, optional
        x coordinates. By default will use ordinal indexes

    mindeg : float
        Below this threshold there is a plateau

    Returns
    =======
    xplateau : int
        Index of the beginning of the plateau
    """
    y = numpy.ravel(y)
    assert numpy.all(numpy.diff(y) >= 0), \
        "y values are not monotonically increasing"
    assert 0.0 <= mindeg <= 90.0, \
        "mindeg must be between 0 and 90 degrees"
    if x is None:
        x = numpy.arange(len(y))
    else:
        x = numpy.ravel(x)
        assert numpy.all(numpy.diff(x) >= 0), \
            "x values are not monotonically increasing"
        x = x[-1] - x[0]
    y = y[-1] - y
    z = numpy.sqrt(x ** 2 + y ** 2)
    rad = numpy.arcsin(y / z)
    deg = rad * 180 / numpy.pi
    # argmax returns the index of the first occurrence of True (the max
    # in a boolean array)
    return numpy.argmax(deg < mindeg)


def _trimplateau(ts, mindeg):
    """
    Utility function. Use `timeseries` directly if you want to find the
    longest plateau for a set of curves in the same story.
    """
    y = ts.values.copy()
    x = ts.index.get_level_values(-1).ravel().astype('M8[h]').astype('int')
    return _findplateau(y, x=x, mindeg=mindeg)


def iterstories(df, freq='H', trim=True, mindeg=1.0):
    """
    This functions returns an iterator over data frames, one for each story.
    Each data frame has two groups of columns, a 'fake' and a 'fact' one. In
    each group there is a column for each cleaned URL in the story.
    """
    df = df.groupby('story_id').apply(_activeusers, freq)
    grouper = df.groupby(level=0)
    i = 1
    for story_id, subdf in grouper:
        subdf = subdf.unstack(level=[1, 2])['active_users']
        subdf = subdf.loc[story_id].fillna(method='ffill').fillna(0)
        if trim:
            # compute plateau for each individual curve; pick the longest and
            # trim all series to the same length
            imax = subdf.apply(_trimplateau, axis=0, args=(mindeg,)).max()
            subdf = subdf.iloc[:imax]
            subdf = subdf.ffill()
        if not subdf.empty:
            # adjust column multi-index and remove those fastidious used in the
            # SQL query to match tweets from Hoaxy
            idx = pandas.MultiIndex.from_tuples(list(subdf.columns))
            subdf.columns = idx   # resets column index
            subdf.rename(columns=lambda k: k.replace('%', ''), inplace=True)
            # finally, yield the data frame and the new story_id
            yield i, subdf
            i += 1


def main(args):
    df = pandas.read_csv(args.input, parse_dates=['created_at'])
    df = filterstories(df, args.min_tweets_total, args.min_tweets_each)
    # Store data frame in HDF5 file, each data frame has its own key
    #   /story_XX
    # where XX is the ID of the story (01, 02, etc.)
    n_stories = len(df['story_id'].unique())
    key_digits = int(math.ceil(math.log10(n_stories)))
    key_template = 'story_{{:0{:d}d}}'.format(key_digits)
    iterator = iterstories(df, freq=args.freq, trim=args.trim,
                           mindeg=args.mindeg)
    store = pandas.HDFStore(args.output, 'w')
    urls = {}
    with store:
        for story_id, story_df in iterator:
            # save the full URLs to dict that will be serialized as JSON,
            # shorten the URL to the domain name. Handle cases when a website
            # occurs multiple times (e.g. infowars.com, infowars.com_1, etc)
            urls[story_id] = defaultdict(list)
            for k, v in story_df.columns:
                urls[story_id][k].append(v)
            counts = defaultdict(count)
            short_columns = [(k, v.split('/')[0])
                             for k, v in story_df.columns]
            for i in range(len(short_columns)):
                k, v = short_columns[i]
                c = counts[v].next()
                if c:
                    v = v + '_{}'.format(str(c))
                    short_columns[i] = (k, v)
            story_df.columns = short_columns
            key = key_template.format(story_id)
            store.put(key, story_df)
    print("Data written to {}.".format(args.output))
    # serialize full URLs to JSON
    output_fname, _ = os.path.splitext(args.output)
    json_output = output_fname + os.path.extsep + 'json'
    with open(json_output, 'w') as f:
        json.dump(urls, f)
    print("Data written to {}.".format(json_output))


if __name__ == '__main__':
    args = parser.parse_args()
    if os.path.exists(args.output) and not args.force_overwrite:
        print("Error: File exists: {}".format(args.output),
              file=sys.stderr)
        sys.exit(1)
    elif args.force_overwrite:
        print("Warning: Overwriting: {}".format(args.output),
              file=sys.stderr)
    main(args)
