""" Report average error from pickled models and data file"""

import os
import numpy
import pandas
import pickle
import glob
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('path', help='path to pickle files')
parser.add_argument('--data', help='override %(metavar)s to data file',
                    dest='data_path', metavar='PATH')
parser.add_argument('--groupby', default='fity0', metavar='KEY',
                    help='report error by %(metavar)s (default: %(default)s)')
args = parser.parse_args()
cwd = os.getcwd()
os.chdir(args.path)

runs = [pickle.load(open(p, 'rb')) for p in glob.glob('*.pickle')]
path = runs[0]['path'] if args.data_path is None else args.data_path
df = pandas.read_csv(path, index_col=0, parse_dates=True)


def err(k, model, metric='mape'):
    _df = df.loc[k]
    data = numpy.c_[_df['fake'], _df['fact']]
    return model.error(data, metric=metric)


metrics = ['mape', 'smape', 'logaccratio', 'rmse']
data = []
labels = []

for run in runs:
    models = run['models']
    del run['models']
    for story, model in models.items():
        tup = []
        for metric in metrics:
            e = err(story, model, metric)
            tup.append(e)
        data.append(tuple(tup))
        label = dict(run)
        label['story'] = story
        labels.append(label)

idx_df = pandas.DataFrame(labels)
del idx_df['path']
del idx_df['seed']
del idx_df['created']
idx_arrays = [idx_df[col] for col in idx_df.columns]
err_df = pandas.DataFrame(data, index=idx_arrays, columns=metrics)
res_df = err_df.groupby(args.groupby).agg(['mean', 'sem'])
print(res_df.round().astype('int'))
os.chdir(cwd)
