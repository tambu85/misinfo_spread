#!/usr/bin/env python

""" Create curves for data fitting. Requires Pandas 0.18+ for new resampling
interface. """

# TODO:
# 2. Report info on discarded stories.


from __future__ import print_function

import os
import sys
import argparse
import pandas
import math
# import numpy
import json
import datetime
from itertools import count
from collections import defaultdict

__all__ = ["parser", "filterstories", "createstore", "iterstories"]

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
parser.add_argument('--max-lag', type=float, default=168.0, help='Keep only'
                    ' stories where fact curve lags fake curve by no more'
                    ' than %(metavar)s. (default: %(default).1f h)',
                    metavar='LAG')


# XXX need to make sure that filter here is made in the same way as Marcella
# script that generated ECDF plots
def filterstories(df, min_tweets_total=1000, min_tweets_each=100, max_lag=168):
    """
    Filter stories from original data to have only

    1. The `fact` curve lags the `fake` curve, not viceversa;
    2. The lag betweet `fact` and `fake` is not larger than `max_lag` hours;
    3. At least a certain number of tweets for each story;
    4. At least a certain number of tweets in each curve for each story.

    Finally, reassign story_id to remove gaps.
    """
    max_lag = datetime.timedelta(hours=max_lag)

    # For each URL we find the first tweet with that URL (based on timestamp).
    cols = ['created_at', 'story_id', 'tweet_type']
    first_df = df.groupby('clean_url').min()[cols].reset_index()

    # Then, since there could be multiple URLs for each story, for each each
    # story and for each type of tweet (fake/fact), we select the earliest URL.
    first_df = first_df.groupby(['story_id', 'tweet_type']).first().unstack()

    # Now we select only the rows where the lag between fact and fake is
    # positive and less than the max lag (default: 186h)
    df_ts = pandas.DataFrame(first_df['created_at'])
    df_ts['lag'] = df_ts['fact'] - df_ts['fake']
    idx = (df_ts['fact'] >= df_ts['fake']) & (df_ts['lag'] <= max_lag)

    # We select the URLs that correspond to those stories, and filter
    # the original data frame to include only rows for those URLs.
    df_urls = pandas.DataFrame(first_df['clean_url'])
    df_urls = df_urls[idx]
    filtered_urls = set(df_urls['fact']).union(df_urls['fake'])  # noqa: W0612
    df = df.query('clean_url in @filtered_urls')

    # Next we compute total number of tweets for each story and for each type
    # of tweet, and filter stories with a min amount of tweets for each type
    # and overall.
    tot_df = df.groupby(['story_id', 'tweet_type']).count()['clean_url']
    tot_df = tot_df.unstack()
    tot_df['total'] = tot_df['fake'] + tot_df['fact']
    tot_df = tot_df.query('fake > @min_tweets_each & '
                          'fact > @min_tweets_each & '
                          'total > @min_tweets_total')
    idx = set(tot_df.index)
    df = df.query('story_id in @idx')

    # Finally, we sort the data frame according to story_id
    df = df.set_index('story_id').sort_index().reset_index()
    return df


def _activeusers(df, freq='H', max_lag=None):
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


def iterstories(df, freq='H', max_lag=None):
    """
    This functions returns an iterator over data frames, one for each story.
    Each data frame has two columns, a 'fake' and a 'fact' one.
    """
    df = df.groupby('story_id').apply(_activeusers, freq, max_lag)
    grouper = df.groupby(level=0)
    for story_id, subdf in grouper:
        subdf = subdf.unstack(level=[1, 2])['active_users']
        subdf = subdf.loc[story_id].fillna(method='ffill').fillna(0)
        if not subdf.empty:
            # adjust column multi-index and remove from URLs any occurrence of
            # the '%' character. It had been used in the SQL query to match
            # tweets from Hoaxy, but now it is not necessary anymore.
            idx = pandas.MultiIndex.from_tuples(list(subdf.columns))
            subdf.columns = idx   # resets column index
            subdf.rename(columns=lambda k: k.replace('%', ''), inplace=True)
            # finally, yield the data frame and the new story_id
            yield story_id, subdf


def createstore(input, output, freq, min_tweets_total,
                min_tweets_each, max_lag, **kwargs):
    """
    This is the main function of the script. It takes all the arguments defined
    by the ArgumentParse and creates a new HDFStore holding the processed data.

    Data will be stored in an HDF5 file, each data frame has its own key
      /story_XX
    where XX is the ID of the story (01, 02, etc.).

    Note: additional keyword arguments are ignored.
    """
    df = pandas.read_csv(input, parse_dates=['created_at'])
    df = filterstories(df, min_tweets_total, min_tweets_each, max_lag)
    n_stories = len(df['story_id'].unique())
    key_digits = int(math.ceil(math.log10(n_stories)))
    key_template = 'story_{{:0{:d}d}}'.format(key_digits)
    iterator = iterstories(df, freq=freq, max_lag=max_lag)
    store = pandas.HDFStore(output, 'w')
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
                c = next(counts[v])
                if c:
                    v = v + '_{}'.format(str(c))
                    short_columns[i] = (k, v)
            story_df.columns = pandas.MultiIndex.from_tuples(short_columns)
            key = key_template.format(story_id)
            store.put(key, story_df)
    print("Data written to {}.".format(output))
    # serialize full URLs to JSON
    output_fname, _ = os.path.splitext(output)
    json_output = output_fname + os.path.extsep + 'json'
    with open(json_output, 'w') as f:
        json.dump(urls, f)
    print("Data written to {}.".format(json_output))


def _main():
    """
    This is the entry point of the script when it is called from the command
    line. It will read arguments from command line and run the actual "main"
    function, and will return whatever it returns.
    """
    args = parser.parse_args()
    if os.path.exists(args.output) and not args.force_overwrite:
        print("Error: File exists: {}".format(args.output),
              file=sys.stderr)
        sys.exit(1)
    elif args.force_overwrite:
        print("Warning: Overwriting: {}".format(args.output),
              file=sys.stderr)
    return createstore(**vars(args))


if __name__ == '__main__':
    _main()
