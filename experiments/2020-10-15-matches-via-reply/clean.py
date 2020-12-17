"""
This script takes in input a spreadsheet of URL pairs, where each pair includes
a URL of a fact-checking website (fact_url) and a URL of a low-credibility
website (fake_url). Each pair has been reviewed by a human annotator, who
checked whether the article in the fact-checking website rated the veracity of
the article in the low-credibility website, and recorded the associated rating
(e.g. true, false, pants on fire, etc.) The script cleans and normalizes the
URL data, consolidates the extracted truth scores, filters out all pairs that
the annotator deemed unrelated (i.e. the "fact" URL is not about, or does not
fact-checks the "fake" URL), and groups together partially overlapping pairs.
These groups of multiple matching pairs represent "stories" that were covered
by multiple fact-checking websites, multiple low-credibility websites, or both.
It then selects the stories where the majority of fact-checkers rated the
low-credibility articles as 'false', and discards from them all the pairs with
a true or missing rating. Finally, it prepares an input file for the SQL query
that will match all tweets with any of these URLs from the Hoaxy database.
"""

import re
import sys
import pandas
import argparse
import networkx
import itertools
import urllib.parse

WAYBACK_PAT = r'.*web\.archive\.org/web/(\d+\*?|\*)/'
WWW_PAT = r'www\.'
AMP_PAT = r'/amp'

RE_SATIRE = re.compile(".*satire.*")
RE_TRUE = re.compile(".*true.*")
RE_FALSE = re.compile(".*false.*")

RATINGS_FALSE = [
    "not true",
    'decontextualized',
    'distorts the facts',
    'fiction',
    'incorrect',
    'miscaptioned',
    'misleading',
    'mostly fiction',
    'outdated',
    'pants on fire',
    'unproven'
]


def _normalizeurl(u):
    """
    Normalize a URL by replacing any fragment and query parameters, and set the
    scheme to http.

    Example:

    Input: https://abc.com/test.html?foo=bar#test
    Output: http://abc.com/test.html
    """
    r = urllib.parse.urlparse(u)
    r = r._replace(scheme="http", fragment="", query="")
    return urllib.parse.urlunparse(r)


def _replace_wayback(col):
    """
    This function performs a number of cleaning steps:
        1. Remove `www.` part
        2. Replace all instances of links to the Internet Archive Wayback
           Machine with the original archived URL.
        3. Remove all extra AMP (Accelerated Mobile Pages) components, e.g.
           cnn.com/amp/hillary-is-dead -> cnn.com/hillary-is-dead.
    """
    def _func(x):
        return (x[col]
                .str
                .replace(WAYBACK_PAT, '')
                .str
                .replace(WWW_PAT, '')
                .str
                .replace(AMP_PAT, ''))
    return _func

# The next functions are just shortcuts for pandas.DataFrame.assign


def _strip(col):
    """
    Return callable that applies string.strip() to column of data frame
    """
    def _func(x):
        return x[col].str.strip()
    return _func


def _lower(col):
    """
    Return callable that applies string.lower() to column of data frame
    """
    def _func(x):
        return x[col].str.lower()
    return _func


def _replace(col, what, value):
    """
    Return callable that applies pandas.DataFrame.replace(what, value) to
    column of data frame
    """
    def _func(x):
        return x[col].replace(what, value)
    return _func


def _storyid(df, proj_col="fake_url"):
    """
    Cluster together similar URLs by following these steps:
    1. Treats matches as edges of a bipartite graph.
    2. Computes projection graph on given column (default: fake URLs).
    3. Finds all connected component on the projection.
    4. The ID of a story is the ID of the associated component.
    """
    G = networkx.from_pandas_edgelist(df, "fake_url", "fact_url")
    G1 = networkx.projected_graph(G, df[proj_col])
    d = {}
    cciter = networkx.connected_components(G1)
    cciter = zip(itertools.count(), cciter)
    for i, cc in cciter:
        for u in cc:
            d[u] = i
    df = df.set_index(proj_col)
    s = pandas.Series(d, index=df.index)
    df['story_id'] = s
    return df.reset_index()


def _majorityfalse(df):
    """
    Computes the overall rating of each story (see above for how stories are
    defined) from the ratings of its fact-checking URLs. A story is "false" if
    the majority of fact-checking URLs in the story report a false rating.
    """
    s = (df
         .drop_duplicates("fact_url")
         .groupby("story_id")
         .rating
         .value_counts())
    df1 = (pandas.DataFrame({'count': s})
           .reset_index()
           .pivot_table(values="count",
                        index="story_id",
                        columns="rating",
                        fill_value=0)
           .assign(total=lambda x: x.sum(axis=1))
           .assign(majfalse=lambda x: x['false'] >= x['total'] / 2)
           )
    df = (df
          .set_index("story_id")
          .assign(consensus_false=df1.majfalse)
          .sort_index(axis=0)
          )
    return df


def read(fp):
    """
    Reads input data and return cleaned data frame. See comments in the source
    code for all the cleaning steps performed.
    """
    print("Reading: {}".format(fp.name), file=sys.stderr)
    df = (pandas.read_excel(fp)
          # Rename columns to lower case, fill spaces with underscore
          .rename(columns=str.lower)
          .rename(columns=lambda k: k.replace(' ', '_'))
          .rename(columns={
              'id_connected_components': 'story_id',
              'truth_score': 'rating',
          })
          # Get only matches (`related` = 1) and drop `related` column
          .query("related == 1")
          .drop("related", axis=1)
          # Drop unnecessary columns (may not be present)
          .drop("notes", axis=1, errors='ignore')
          .drop("unnamed:_8", axis=1, errors='ignore')
          .drop("unnamed:_9", axis=1, errors='ignore')
          .drop("new_fact_url", axis=1, errors='ignore')
          .drop("new_fake_url", axis=1, errors='ignore')
          .drop("connected_components", axis=1, errors='ignore')
          # Clean rating values and transform to categorical
          .assign(rating=_strip("rating"))
          .assign(rating=lambda x: x['rating'].fillna("False"))
          .assign(rating=_lower("rating"))
          .assign(rating=_replace("rating", RE_SATIRE, "satire"))
          .assign(rating=_replace("rating", RE_FALSE, "false"))
          .assign(rating=_replace("rating", RATINGS_FALSE, "false"))
          .assign(rating=_replace("rating", "half true", "mixture"))
          .assign(rating=_replace("rating", RE_TRUE, "true"))
          .assign(rating=lambda x: x['rating'])
          # Normalize URLs to same scheme and remove query/fragments
          .assign(fake_url=_replace_wayback("fake_url"))
          .assign(fact_url=_replace_wayback("fact_url"))
          .assign(fake_url=lambda x: x['fake_url'].apply(_normalizeurl))
          .assign(fact_url=lambda x: x['fact_url'].apply(_normalizeurl))
          # Cluster matches into stories
          .pipe(_storyid)
          # Compute the rating for each story and set index to story ID
          .pipe(_majorityfalse)
          )
    return df


def _makeurlpattern(u):
    """
    Transform a URL in a pattern for SQL's `like' operator. This is to allow
    matching variants of the same URL.

    Example:
    http://snopes.com/hello-world -> %snopes.com/%hello-world%
    """
    r = urllib.parse.urlparse(u)
    pat = r.netloc.strip('/') + '/%' + r.path.strip('/') + '%'
    return pat


def write(df, fp=None):
    """
    Filter out data that does not correspond to false stories and convert URLs
    into patterns for the SQL query. (See
    replication/00_data_collection/match_tweets.sql)
    """
    df1 = (df
           # Filter out matches where the rating by the fact-checker is not
           # `false`, or where there is no consensus among fact-checkers that
           # the story is false
           .query("rating == 'false' and consensus_false == True")
           # Select columns for query
           .drop_duplicates(['fake_url', 'fact_url'])
           .assign(fake_url=lambda x: x['fake_url'].apply(_makeurlpattern))
           .assign(fact_url=lambda x: x['fact_url'].apply(_makeurlpattern))
           .get(["fake_url", "fact_url"]))
    if fp is not None:
        with fp:
            df1.to_csv(fp)
        print("Written: {}".format(fp.name), file=sys.stderr)
    return df1


def make_parser():
    """
    Create parser for reading arguments from the command line.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path",
                        type=argparse.FileType('rb'),
                        help="Path to input file (Excel)")
    parser.add_argument("-o",
                        "--output",
                        default=sys.stdout,
                        metavar="PATH",
                        type=argparse.FileType("w"),
                        help="Write query data to file (CSV) "
                        "(default: standard output)")
    return parser


if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    df0 = read(args.path)
    df1 = write(df0, args.output)
