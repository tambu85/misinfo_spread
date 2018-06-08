-- This script retrieves the tweets that include one or more URLs from the list
-- of matched "fake news" and "fact-checking" articles in Hoaxy. It reads a
-- list of matches in CSV format from disk using psql's \copy command. The CSV
-- file must be in 'matching_export_of_merge_sheet.csv'. This file name can be
-- changed to a different path, if needed.

-- *****************************************************************************
--                                HOW TO RUN:
-- *****************************************************************************
--
-- ssh -fNL 5433:recall.ils.indiana.edu:5433: smithers.cs.indiana.edu
-- psql -q -h localhost -p 5433 -d hoaxy -u gciampag < match_tweets.sql >
-- output.csv
-- *****************************************************************************

-- Temporary table to hold the matches data. URLs here will be joined against
-- the `article` table of Hoaxy, and matched against the `canonical_url`
-- column in that table.
create temporary table matches (
    story_id int,
    fake_url varchar,
    fact_url varchar
);
\copy matches from './matching_export_of_merge_sheet.csv' csv header;

-- Create at temporary view for the join operation. Two things are noteworthy
-- here: 
-- 1) Both `fact_url` and `fake_url` columns contain duplicates, since
--    the mapping is a many-to-many one. So we need to use DISTINCT. 
-- 2) The match with `canonical_url` need to match also the initial
--    `http[s]://` part, which is not present in the CSV data. So we need to
--    prepend and append the character '%' to make sure that the match occurs.
-- 3) We include the story_id and a categorical variable to sort easily the
--    tweets at a later stage.
create temporary view _matches (story_id, pattern, clean_url, tweet_type)
as (
    select distinct
        story_id,
        concat('%', matches.fake_url, '%') as pattern,
        matches.fake_url,
        'fake'

    from 
        matches
    union
    select distinct
        story_id,
        concat('%', matches.fact_url, '%') as pattern,
        matches.fact_url,
        'fact'
    from
        matches
);

-- The main query. We create a temporary view so that it can be copied to
-- standard output later using psql's \copy command. Note that the distinct
-- condition makes sure that no tweet is counted more than once for each given
-- story. This is to make sure that tweets with multiple URLs (like quoted
-- tweets with a URL in either the quoting or quoted status, or a status with
-- multiple URLs) do not account for multiple instances. 
create temporary view results 
as (
    select distinct on (
            tweet_id, 
            story_id
        )
        tweet.json_data->>'id_str' as tweet_id,
        tweet.json_data->'user'->>'id_str' as user_id,
        tweet.created_at,
        _matches.clean_url,
        _matches.story_id,
        _matches.tweet_type
    from 
        tweet 
    join 
        ass_tweet_url 
    on 
        tweet.id = ass_tweet_url.tweet_id 
    join url 
    on 
        url.id = ass_tweet_url.url_id 
    join 
        article 
    on 
        url.article_id = article.id 
    join 
        _matches
    on 
        canonical_url like _matches.pattern
    where 
        article.group_id is not null 
);

\COPY (SELECT * FROM results) TO stdout WITH CSV HEADER

-- drop view results cascade;
-- drop view matched_patterns cascade;
-- drop table matches cascade;
-- drop view results;
