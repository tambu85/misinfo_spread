
###########
import pandas as pd
import numpy as np

list_of_files = ['4th-mysterious-death-connected-to-the-dnc',
                 'alicia-machado-adult-star',
                 'bill-clinton-illegitimate-son',
                 'black-lives-matter-protesters-chant-for-dead-cops-now-in-baton-rouge',
                 'black-protesters-targeted-whites-in-milwaukee',
                 'clinton-byrd-photo-klan',
                 'clinton-compliant-citizenry',
                 'clintons_zeifman',
                 'debate-secret-hand-signals',
                 'deray-mckesson-and-the-summer-of-chaos',
                 'dnc-hiring-actors-via-craigslist-to-replace-delegates',
                 'dr-drew-hillary-clinton-health',
                 'flags-banned-at-dnc',
                 'google-manipulate-hillary-clinton',
                 'hillary-clinton-freed-child-rapist-laughed-about-it',
                 'hillary-clinton-has-parkinsons-disease',
                 'hillary-clinton-medical-records-leaked',
                 'hillary-clinton-secret-earpiece',
                 'hillary-clinton-seizure-video',
                 'julian-assange-bernie-sanders-was-threatened',
                 'khizr-khan-375000-clinton-foundation',
                 'khizr-khan-is-a-muslim-brotherhood-agent',
                 'mexico-border-trump-elected',
                 'michael-savage-removed',
                 'muslims-in-japan',
                 'politics-sites-mismatched-clinton-rally-image-goes-viral',
                 'satire_sharia',
                 'seth-conrad-rich',
                 'three-syrian-refugees-assault-5-year-old-girl-at-knifepoint',
                 'tim-kaine-white-people-minority',
                 'yokohillary']

path_file ="/Users/marcella/PycharmProjects/untitled/fit/"

for item in list_of_files:

    time = []
    aux_for_users = []
    aux_BA = []
    aux_against_users = []
    aux_FA = []

    time2 = []
    aux_for_users2 = []
    aux_BA2 = []
    aux_against_users2 = []
    aux_FA2 = []

    name1 = path_file + item + '_without_segregation.out'
    name2 = path_file + item + '_with_segregation.out'

    with open(name1) as f:
        ct = 0
        for line in f:
            wline = line.split(' ')
            if ct == 0:
                time = np.array(wline, dtype=float)
            if ct == 1:
                aux_for_users = np.array(wline, dtype=float)
            if ct == 2:
                aux_BA = np.array(wline, dtype=float)
            if ct == 3:
                aux_against_users = np.array(wline, dtype=float)
            if ct == 4:
                aux_FA = np.array(wline, dtype=float)
            ct = ct + 1

    with open(name2) as f:
        ct = 0
        for line in f:
            wline = line.split(' ')
            if ct == 0:
                time2 = np.array(wline, dtype=float)
            if ct == 1:
                aux_for_users2 = np.array(wline, dtype=float)
            if ct == 2:
                aux_BA2 = np.array(wline, dtype=float)
            if ct == 3:
                aux_against_users2 = np.array(wline, dtype=float)
            if ct == 4:
                aux_FA2 = np.array(wline, dtype=float)
            ct = ct + 1


    raw_data1 = {'Date': time,
                'For_empirico': aux_for_users,
                'For_BA': aux_BA,
                'Against_empirico': aux_against_users,
                'Against_FA': aux_FA}

    raw_data2 = {'Date': time2,
                 'For_empirico': aux_for_users2,
                 'For_BA': aux_BA2,
                 'Against_empirico': aux_against_users2,
                 'Against_FA': aux_FA2}

    df1 = pd.DataFrame(raw_data1, columns=["Date", "For_empirico", "For_BA", "Against_empirico", "Against_FA"])
    df1.to_csv(str(name1).replace('.out', '.csv'), index=False)

    df2 = pd.DataFrame(raw_data2, columns=["Date", "For_empirico", "For_BA", "Against_empirico", "Against_FA"])
    df2.to_csv(str(name2).replace('.out', '.csv'), index=False)
