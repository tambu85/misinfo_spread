""" Clean annotated matches spreadsheet """

import re
import sys
import csv
import pandas
import argparse
import networkx
import itertools
import urllib.parse

WAYBACK_PAT = r'.*web\.archive\.org/web/\d+/'
WWW_PAT = r'www\.'

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

COLS = ['story_id',
        'fake_url',
        'fake_title',
        'fake_tweet',
        'fact_url',
        'fact_title',
        'fact_tweet',
        'rating',
        'consensus_false'
        ]


def _normalizeurl(u):
    r = urllib.parse.urlparse(u)
    r = r._replace(scheme="http", fragment="", query="")
    return urllib.parse.urlunparse(r)


def _replace_wayback(col):
    def _func(x):
        return (x[col]
                .str
                .replace(WAYBACK_PAT, '')
                .str
                .replace(WWW_PAT, ''))
    return _func


def _strip(col):
    def _func(x):
        return x[col].str.strip()
    return _func


def _lower(col):
    def _func(x):
        return x[col].str.lower()
    return _func


def _replace(col, what, value):
    def _func(x):
        return x[col].replace(what, value)
    return _func


def _storyid(df):
    proj_col = "fake_url"
    G = networkx.from_pandas_dataframe(df, "fake_url", "fact_url")
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
          .assign(consensus_false=df1.majfalse))
    return df


def read(fp):
    df = (pandas.read_excel(fp)
          # Rename columns to lower case, fill spaces with underscore
          .rename(columns=str.lower)
          .rename(columns=lambda k: k.replace(' ', '_'))
          .rename(columns={
              'id_connected_components': 'story_id',
              'truth_score': 'rating',
          })
          # Drop unnecessary columns (may not be present)
          .drop("notes", axis=1, errors='ignore')
          .drop("unnamed:_8", axis=1, errors='ignore')
          .drop("unnamed:_9", axis=1, errors='ignore')
          .drop("new_fact_url", axis=1, errors='ignore')
          .drop("new_fake_url", axis=1, errors='ignore')
          .drop("connected_components", axis=1, errors='ignore')
          # Get only matches and drop related column
          .query("related == 1")
          .drop("related", axis=1)
          # Clean rating values and transform to categorical
          .assign(rating=_strip("rating"))
          .assign(rating=lambda x: x['rating'].fillna("False"))
          .assign(rating=_lower("rating"))
          .assign(rating=_replace("rating", RE_SATIRE, "satire"))
          .assign(rating=_replace("rating", RE_FALSE, "false"))
          .assign(rating=_replace("rating", RATINGS_FALSE, "false"))
          .assign(rating=_replace("rating", "half true", "mixture"))
          .assign(rating=_replace("rating", RE_TRUE, "true"))
          .assign(rating=lambda x: x['rating'].astype('category'))
          # Normalize URLs to same scheme and remove query/fragments
          .assign(fake_url=_replace_wayback("fake_url"))
          .assign(fact_url=_replace_wayback("fact_url"))
          .assign(fake_url=lambda x: x['fake_url'].apply(_normalizeurl))
          .assign(fact_url=lambda x: x['fact_url'].apply(_normalizeurl))
          # Recompute story_id
          .pipe(_storyid)
          .pipe(_majorityfalse)
          .sort_index(axis=0)
          .reset_index()
          # .query("majfalse == True")
          # .drop("majfalse", axis=1)
          )
    return df[COLS]


def write(df):
    return (df
            .drop_duplicates(['fake_url', 'fact_url'])
            .drop(['fake_tweet', 'fact_tweet'], axis=1)
            .reset_index())


def make_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path",
                        type=argparse.FileType('rb'),
                        help="Path to input file (Excel)")
    parser.add_argument("-o",
                        "--output",
                        default=sys.stdout,
                        type=argparse.FileType("w"),
                        help="Path to output file (CSV)")
    return parser


if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    print("Reading: {}".format(args.path.name))
    df0 = read(args.path)
    df1 = write(df0)
    df0.to_csv(args.output, quoting=csv.QUOTE_ALL, index=False)
    print("Written: {}".format(args.output.name))
