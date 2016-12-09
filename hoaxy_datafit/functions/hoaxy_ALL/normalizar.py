#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import matplotlib.pyplot as plt

file=['hoaxy_4th-mysterious-death-connected-to-the-dnc_cum.csv','hoaxy_alicia-machado-adult-star_cum.csv','hoaxy_bill-clinton-illegitimate-son_cum.csv','hoaxy_black-lives-matter-protesters-chant-for-dead-cops-now-in-baton-rouge_cum.csv','hoaxy_black-protesters-targeted-whites-in-milwaukee_cum.csv','hoaxy_clinton-byrd-photo-klan_cum.csv','hoaxy_clinton-compliant-citizenry_cum.csv','hoaxy_clinton-secret-earpiece-debate_cum.csv','hoaxy_clintons_zeifman_cum.csv','hoaxy_debate-secret-hand-signals_cum.csv','hoaxy_deray-mckesson-and-the-summer-of-chaos_cum.csv','hoaxy_dnc-hiring-actors-via-craigslist-to-replace-delegates_cum.csv','hoaxy_dr-drew-hillary-clinton-health_cum.csv','hoaxy_flags-banned-at-dnc_cum.csv','hoaxy_google-manipulate-hillary-clinton_cum.csv','hoaxy_hillary-clinton-freed-child-rapist-laughed-about-it_cum.csv','hoaxy_hillary-clinton-has-parkinsons-disease_cum.csv','hoaxy_hillary-clinton-medical-records-leaked_cum.csv','hoaxy_hillary-clinton-secret-earpiece_cum.csv','hoaxy_hillary-clinton-seizure-video_cum.csv','hoaxy_julian-assange-bernie-sanders-was-threatened_cum.csv','hoaxy_khizr-khan-375000-clinton-foundation_cum.csv','hoaxy_khizr-khan-is-a-muslim-brotherhood-agent_cum.csv','hoaxy_mexico-border-trump-elected_cum.csv','hoaxy_mexico-border-trump-elected_cum_day.csv','hoaxy_mexico-border-trump-elected_cum_hour.csv','hoaxy_michael-savage-removed_cum.csv','hoaxy_muslims-in-japan_cum.csv','hoaxy_politics-sites-mismatched-clinton-rally-image-goes-viral_cum.csv','hoaxy_satire_sharia_cum.csv','hoaxy_seth-conrad-rich_cum.csv','hoaxy_three-syrian-refugees-assault-5-year-old-girl-at-knifepoint_cum.csv','hoaxy_tim-kaine-white-people-minority_cum.csv','hoaxy_yokohillary_cum.csv']
for item in file:
	print item
	input_data=pd.read_csv(item,index_col=None,delimiter=',')
	data_FOR=np.array(input_data.For)
	data_AGAINST=np.array(input_data.Against)
	t_data=np.arange(0,len(data_FOR))
	For_mean=np.mean(data_FOR)
	Against_mean=np.mean(data_AGAINST)
	For_std=np.std(data_FOR)
	Against_std=np.mean(data_AGAINST)

	for_new=(data_FOR-For_mean)/For_std
	against_new=(data_AGAINST-Against_mean)/Against_std	
	print item,for_new
	# plt.plot(t_data, against_new)
	# plt.show()