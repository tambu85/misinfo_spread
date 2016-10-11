
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urlparse import urlparse
import pandas as pd
from datetime import datetime


filename="tweets_timeline_revised.csv"
hoaxy_data = pd.read_csv(filename,parse_dates=True)
snopes_url = hoaxy_data['snopes_page_url']
time=hoaxy_data['tweet_created_at']
type=hoaxy_data['tweet_type']
user=hoaxy_data['tweet_user_id']

url_dict={}

#create a dictionary to count the occurrences of each "topic" (fake or debunking)
for i in range(len(hoaxy_data)) :

    if snopes_url[i] is not None:
        url=snopes_url[i]

        if url in url_dict:
            url_dict[url] += 1
        else:
            url_dict[url] = 1

#select only URLs with more than 1000 total occurences

for keyurl in url_dict:
    if url_dict[keyurl]>1000 :
        topic = urlparse(keyurl).path
        csvfile = "hoaxy_" + topic.strip('/').lstrip('/') + ".csv"

        print(url_dict[keyurl]) #number of occurrences
        print(topic)

        for_time_dict={}
        against_time_dict={}

        for i in range(len(hoaxy_data)) :
            if(snopes_url[i]==keyurl): #for every single selected topic...

               d=datetime.strptime(time[i],'%Y-%m-%d %H:%M:%S')

               #UNCOMMENT each 12 hours
               #if(d.hour<12):
               #    h=' 00'
               #elif(d.hour>=12):
               #    h=' 12'

               key = datetime.strftime(d, '%Y-%m-%d')  # +h


               #create two dictionaries, FOR and AGAINST with list of users aggregated by time interval
               if (type[i] == "fake_news"):
                   if key in for_time_dict:
                       for_time_dict[key].append(user[i])
                   else:
                        for_time_dict[key]=[]
                        for_time_dict[key].append(user[i])
               elif (type[i] == "fact_checking"):
                    if key in against_time_dict:
                        against_time_dict[key].append(user[i])
                    else:
                        against_time_dict[key] = []
                        against_time_dict[key].append(user[i])


        # add missing days (days with no posts) among the min and max dates
        min_date = min(min(for_time_dict.keys()), min(against_time_dict.keys()))
        max_date = max(max(for_time_dict.keys()), max(against_time_dict.keys()))
        print(min_date)
        print(max_date)
        idx = pd.date_range(min_date, max_date) #,freq='12H')

        for dd in idx:
            date = datetime.strftime(dd, '%Y-%m-%d')
            if date not in for_time_dict:
                for_time_dict[date]=[]
            if date not in against_time_dict:
                against_time_dict[date]=[]

        #transform in data frame and write it in the csv
        df = pd.DataFrame(columns=('Date','For', 'Against'))

        i=0
        for keytime in for_time_dict:
            df.loc[i]=[keytime,float(len(set(for_time_dict[keytime]))),float(len(set(against_time_dict[keytime])))]
            i += 1

        df = df.sort_values(by='Date')
        df.to_csv(csvfile, index=False)















