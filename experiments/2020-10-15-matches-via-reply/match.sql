create temp table res as 
    select 
        article.title as fact_title,
        article2.title as fake_title,
        article.canonical_url as fact_url,
        article2.canonical_url as fake_url,
        /* article.content as fact_body, */
        /* article2.content as fake_body, */
        /* coalesce(url.canonical, url.expanded, url.raw) as fact_url, */
        /* coalesce(url2.canonical, url2.expanded, url2.raw) as fake_url, */
        tweet.json_data::json->'text' as fact_tweet,
        tweet2.json_data::json-> 'text' as fake_tweet
    from 
        url 
    join 
        site 
    on 
        url.site_id = site.id 
    join 
        ass_tweet_url
    on 
        url.id = ass_tweet_url.url_id
    join 
        tweet 
    on 
        tweet.id = ass_tweet_url.tweet_id 
    join 
        ass_tweet 
    on 
        ass_tweet.id = tweet.id 
    join 
        tweet as tweet2 
    on 
        ass_tweet.in_reply_to_status_id = tweet2.raw_id 
    join 
        ass_tweet_url as ass_tweet_url2
    on
        ass_tweet_url2.tweet_id = tweet2.id
    join
        url as url2
    on
        ass_tweet_url2.url_id = url2.id
    join
        site as site2
    on
        url2.site_id = site2.id
    join
        article
    on
        url.article_id = article.id
    join
        article as article2
    on 
        url2.article_id = article2.id
    where 
        site.site_type = 'fact_checking' 
    and 
        site2.site_type = 'claim'
;
\copy (select * from res) to './matches.csv' with csv header
