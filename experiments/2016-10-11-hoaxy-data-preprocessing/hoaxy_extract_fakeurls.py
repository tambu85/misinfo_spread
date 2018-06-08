#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Read the data and create csv files for the hoax with more than 1000 total
occurrences. uncomment some lines to change time granularity (by day, by hour)
"""

from datetime import datetime
import pandas as pd

filename = "tweets_timeline_185.csv"
hoaxy_data = pd.read_csv(filename, parse_dates=True)
snopes_url = hoaxy_data['snopes_page_url']
fake_url = hoaxy_data['fake_page_url']
time = hoaxy_data['tweet_created_at']
type = hoaxy_data['tweet_type']
user = hoaxy_data['tweet_user_id']

url_dict = {}

# create a dictionary to count the occurrences of each "topic" (fake or
# debunking)
for i in range(len(hoaxy_data)):

    if snopes_url[i] is not None:
        url = snopes_url[i]

        if url in url_dict:
            url_dict[url] += 1
        else:
            url_dict[url] = 1


i = 0
index = []
fake_tot = []
debunking_tot = []

# select only URLs with more than 1000 total occurences
for keyurl in url_dict:
    if url_dict[keyurl] > 1000:
        i = i + 1
        index.append(i)
        print("******")
        print(str(i))
        print(keyurl)
        print(str(url_dict[keyurl]))
        fake_dict = {}
        fake = 0
        debunking = 0
        min_date = datetime(2017, 1, 1)
        max_date = datetime(2016, 1, 1)
        for j in range(len(hoaxy_data)):
            # print(j)

            if (snopes_url[j] == keyurl):  # for every single selected topic...
                d = datetime.strptime(time[j], '%Y-%m-%d %H:%M:%S')
                if(d < min_date):
                    min_date = d
                if(d > max_date):
                    max_date = d

                # UNCOMMENT each 12 hours
                # if(d.hour<12):
                #    h=' 00'
                # elif(d.hour>=12):
                #    h=' 12'

                # key = datetime.strftime(d, '%Y-%m-%d %H')  # +h
                key = datetime.strftime(d, '%Y-%m-%d')  # +h

                if(type[j] == "fake_news"):
                    fake = fake + 1
                    if fake_url[j] is not None:
                        url = fake_url[j]
                        if url in fake_dict:
                            fake_dict[url] += 1
                        else:
                            fake_dict[url] = 1

                elif(type[j] == "fact_checking"):
                    debunking = debunking + 1
        fake_tot.append(fake)
        debunking_tot.append(debunking)
        print("TOT FAKE:" + str(fake))
        print("TOT DEBUNKING:" + str(debunking))
        print("MIN DATE:" + str(min_date))
        print("MAX DATE:" + str(max_date))
        print("---RELATED FAKE URLS---")
        for key_fakeurl in fake_dict:
            print(key_fakeurl)
            print(str(fake_dict[key_fakeurl]))
            print("...")

print("---------")
print(index)
print("---------")
print(fake_tot)
print("---------")
print(debunking_tot)
print("---------")
myTable = pd.DataFrame(index,
                       fake_tot,
                       debunking_tot,
                       columns=['STORY',
                                'FAKE NEWS TWEETS',
                                'FACT CHECKING TWEETS'])
print(myTable)
