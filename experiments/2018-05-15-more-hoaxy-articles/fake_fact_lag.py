import pandas
import numpy as np
from statsmodels.distributions.empirical_distribution import ECDF
import datetime
import matplotlib.pyplot as plt

tweets_path = '../../data/match_tweets.csv'

tweets = pandas.read_csv(tweets_path)
print(tweets.columns)

story_ids=set(tweets['story_id'])
print(story_ids)
diff = []

for story in story_ids:
    fact_list = tweets[(tweets.story_id == story) & (tweets.tweet_type == 'fact')]
    fake_list = tweets[(tweets.story_id == story) & (tweets.tweet_type == 'fake')]
    if len(fact_list) > 0 and len(fake_list) > 0:
        min_fact = min(fact_list['created_at'])
        min_fake = min(fake_list['created_at'])
        minfact = datetime.datetime.strptime(min_fact, '%Y-%m-%d %H:%M:%S')
        minfake = datetime.datetime.strptime(min_fake, '%Y-%m-%d %H:%M:%S')
        d = (minfact-minfake)
        d_hours = (minfact - minfake).total_seconds() / 3600.0

        if(d_hours>0):
            diff.append(d_hours)


def empirical_cdf(data):
    percentiles = []
    n = len(diff)
    sort_data = np.sort(data)

    for i in np.arange(1, n + 1):
        p = i / n
        percentiles.append(p)
    return sort_data, percentiles


# use the function on the setosa iris data
diff_sort, diff_percentiles = empirical_cdf(diff)

print(diff_sort)

plt.step(diff_sort,diff_percentiles, label='Lag (hours)',color = 'blue')
plt.axvline(x=168,linewidth=2, color='r')
plt.title('Fake-Fact Lag')
plt.xlabel(r'Lag $\tau$ (h)')
plt.ylabel(r'$Pr\{\Delta t \leq \tau\}$')
plt.show()

plt.figure()
plt.hist(diff)
plt.title("Fake-Fact Lag")
plt.xlabel("Lag (hours)")
plt.ylabel("Frequency")
plt.show()