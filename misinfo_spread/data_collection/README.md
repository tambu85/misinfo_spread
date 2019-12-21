Instructions
============

1. Run SQL query [sql/top_claim_articles.sql](sql/top_claim_articles.sql) to xport the 100 most tweeted articles collected by Hoaxy:

```bash
    # Create SSH tunnel to your database. In this case need to tunnel through intermediate host (smithers)
    ssh -fNL 5433:recall.ils.indiana.edu:5433 smithers
    # Run SQL query
    psql -q -h localhost -p 5433 -d hoaxy -U gciampag < top_claim_articles.sql
```

2. Manually search matching fact-checking articles on Snopes, PolitiFact, and FactCheck.org using [Google Search (custom search)](cse.google.com/cse/publicurl?cx=012347910696195860803:mh7emrnq-c4) or Google's [Fact Check Explorer](https://toolbox.google.com/factcheck/explorer). (Note: this one may return results from additional fact-checking websites;)

3. Record the URLs of the matching articles [in a spreadsheet](https://docs.google.com/spreadsheets/d/1UUA57bUTRGkc65OUj-YMsFdJs6q2r4B_5HY8LMljdPk/edit?usp=sharing);

4. Export spreadsheet to CSV format to `csv/matching_export_of_merge_sheet.csv`.

5. Run SQL query [sql/match_tweets.sql](sql/match_tweets.sql) on Hoaxy database. This will fetch all tweets from either the fact-checking or "fake news" articles:

```shell
    # Create SSH tunnel to your database. In this case need to tunnel through intermediate host (smithers)
    ssh -fNL 5433:recall.ils.indiana.edu:5433 smithers
    # Run SQL query
    psql -q -h localhost -p 5433 -d hoaxy -U gciampag < match_tweets.sql  | pigz -fc > ../data_cleaning/match_tweets.csv.gz
```

6. The tweets need to be pre-processed and filtered. This is done in the `data_cleaning` folder. See its own [README](../data_cleaning/README.md) for instructions.
