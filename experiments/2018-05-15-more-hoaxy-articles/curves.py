#!/usr/bin/env python

""" Create curves for data fitting. Requires Pandas 0.18+ for new resampling
interface. """

from __future__ import print_function

import os
import sys
import argparse
import pandas
import datetime

__all__ = ["parser", "filterstories", "createdata"]

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
parser.add_argument('--max-lag', type=int, default=168, help='Keep only'
                    ' stories where fact curve lags fake curve by no more'
                    ' than %(metavar)s. (default: %(default).1f h)',
                    metavar='LAG')


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
    cols = ['story_id', 'tweet_type', 'created_at']
    first_tweet_df = df.groupby('clean_url').min()[cols]
    first_tweet_df.reset_index(inplace=True)

    # Sort the tweets by story_id, tweet_type, and timestamp
    first_tweet_df.sort_values(cols, inplace=True)

    # Then, since there could be multiple URLs for each story and for each type
    # of tweet (fake/fact), we group by and select the first row. Because we
    # sorted before by timestamp, this is the URL with the smallest timestamp.
    first_tweet_df = first_tweet_df.groupby(['story_id', 'tweet_type']).first()

    # Now, for each story there are exactly two rows (one for fact and one for
    # fake). We can thus unstack on tweet_type and obtain a data frame with one
    # column for fact and one for fake. (Actually we obtain a multiindex since
    # there were already two columns --- the timestamp (created_at), and the
    # URL (clean_url).
    first_tweet_df = first_tweet_df.unstack()

    # We can get rid of the multiindex on the columns by simply creating two
    # separate data frames.
    df_ts = pandas.DataFrame(first_tweet_df['created_at'])
    df_urls = pandas.DataFrame(first_tweet_df['clean_url'])

    # Using the timestamp data frame, we can compute the lag between the
    # publication of the fact URL and the publication of the fake URL. (For
    # simplicity the time of publication is approximately the same as that of
    # the first tweet.)
    df_ts['lag'] = df_ts['fact'] - df_ts['fake']

    # We can now select only the stories where the lag between fact and fake is
    # positive and less than the max lag (default: 168h). We put this info into
    # a boolean frame that can be used as an index.
    idx = (df_ts['fact'] >= df_ts['fake']) & (df_ts['lag'] <= max_lag)

    # Using the index, we select the URLs of the filtered stories, and finally
    # can go back and filter the original data frame of tweets, so that it
    # includes only rows for those URLs.
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

    # Finally, we sort the data frame according to story_id, reset the index,
    # and return it.
    df = df.set_index('story_id').sort_index().reset_index()
    return df


def _resample(df, lag, freq):
    """
    Compute curves to fit. Data are number of unique users tweet at hourly
    frequency. (This is taken to represent the number of "active"
    believers/fact-checkers at time t.)
    """
    df.set_index('created_at', inplace=True)
    df = df.resample('h').agg({'tweet_id': 'count'})
    df = df.rename(columns={'tweet_id': 'active_users'})
    t0 = df.index[0]
    idx = pandas.date_range(start=t0, periods=lag, freq=freq)
    df = df.reindex(idx)
    return df.fillna(0).cumsum()


def _align(df, lag):
    """
    For each story, create a single data frame by aligning the 'fact' curve to
    the 'fake' curve.
    """
    story_id = df.index.get_level_values(0)[0]
    a = df.loc[story_id, 'fake']
    b = df.loc[story_id, 'fact']
    a, b = a.align(b)
    df = pandas.DataFrame({'fake': list(a['active_users'][:lag]),
                           'fact': list(b['active_users'][:lag])},
                          index=a[:lag].index)
    df.fillna(0, inplace=True)
    return df


def createdata(input, output, freq, min_tweets_total, min_tweets_each,
               max_lag, **kwargs):
    """
    This is the main function of the script. It takes all the arguments defined
    by the ArgumentParse and create the data files.

    Note: additional keyword arguments are ignored.
    """
    df = pandas.read_csv(input, parse_dates=['created_at'])
    df = filterstories(df, min_tweets_total, min_tweets_each, max_lag)

    df1 = df.groupby(['story_id', 'tweet_type']).apply(_resample,
                                                       max_lag, freq)
    df1.index.rename('timestamp', level=-1, inplace=True)
    df2 = df1.groupby('story_id').apply(_align, max_lag)
    df2.reset_index(inplace=True)
    df2.to_csv(output, index=False)
    print("Data written to {}.".format(output))

    # serialize full URLs to JSON
    output_fname, _ = os.path.splitext(output)
    urls_output = output_fname + '_urls' + os.path.extsep + 'csv'
    urls_df = df.groupby(['story_id', 'tweet_type']).first()['clean_url']
    urls_df = urls_df.unstack()
    urls_df.replace('%', '', regex=True, inplace=True)
    urls_df.to_csv(urls_output)
    print("Data written to {}.".format(urls_output))


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
    return createdata(**vars(args))


if __name__ == '__main__':
    _main()
