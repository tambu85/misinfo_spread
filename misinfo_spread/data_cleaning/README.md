Instructions
============

1. These steps should follow the data collection phase, which is documented in `../data_collection/README.md`. You should have the data in a file called `match_tweets.csv.gz` (not included in this repository due to [Twitter Developer Policy (F.2.2)](https://developer.twitter.com/en/developer-terms/policy#f-be-a-good-partner-to-twitter) \[[Internet Archive](https://web.archive.org/web/20191221184030/https://developer.twitter.com/en/developer-terms/policy#f-be-a-good-partner-to-twitter)\]).

2. First of all, you need to decide a value for the lag between the publication of fact-checking articles and that of "fake news" articles. To do so, run `fake_fact_lag.py`. This will plot the empirical CDF of the lag distribution (for each story). In the paper, the lag was set to 168 hours (1 week).

3. Now you can generate the "fake" and "fact" curves for fitting. To do so, run `curves.py`. The script can perform some filtering to remove stories with few tweets. The data in the paper were generated with the following parameters:

```sh

python curves.py -f h --min-tweets-each 100 --min-tweets-total 1000 ./match_tweets.csv.gz data_tweets.csv
```

4. You should have now two files: one called `data_tweets.csv` (the actual data) and another called `data_tweets_urls.csv`, which lists the URLs selected for the "fake" and "fact" curve, respectively.

5. You can plot all the data using the script `plotall.py`:

```sh

python plotall.py data_tweets.csv
```
