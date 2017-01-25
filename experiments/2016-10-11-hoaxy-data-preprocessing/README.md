# Preprocessing of Hoaxy data

Python files to preprocess hoaxy data in "tweets_timeline_revised.csv", a csv where in each row it is reported:

tweet_created_at: timestamp of this tweet

tweet_id: id of this tweet

tweet_user_id: user_id that posts this tweet

tweet_type: type of this tweet, either 'fact_checking' or 'fake_news'

snope_page_url: if this tweet is 'fact_checking', the posted url is snope_page_url; else the snope_page_url is fact_checking page of the posted fake urls.

fake_page_url: if this tweet is 'fact_checking', it is null; if this tweet is 'fake_news', the posted url is fake_page_url. 


## Instructions

1.  Run "hoaxy_preproc.py", and it will create a csv for the hoaxes with more than 1000 occurrences. In the csv files, for each raw: the date (day or every 12 hours, depending on how we set the code), the number of fake tweets and the number of factcheck tweets. 

2.  Run "hoaxy_cumulative.py" to create the csv files with cumulative data

3.  Run "hoaxy_plot.py" and "hoaxy_scatter.py" to generate the plots.
