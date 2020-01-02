import numpy
import pandas
import pickle
import glob

runs = [pickle.load(open(p, 'rb')) for p in glob.glob('*.pickle')]
runs = runs[2:]
path = runs[0]['path']
df = pandas.read_csv(path, index_col=0, parse_dates=True)

def err(k, model, metric='mape'):
    _df = df.loc[k]
    data = numpy.c_[_df['fake'], _df['fact']]
    return model.error(data, metric=metric)

labels = []
values = []

for run in runs:
    fit_type = run['fity0']
    models = run['models']
    for story, model in models.items():
        for metric in ['mape', 'smape', 'logaccratio']:
            label = (metric, fit_type, story)
            e = err(story, model, metric)
            labels.append(label)
            values.append(e)
        metric = 'rmse'
        label = (metric, fit_type, story)
        e = numpy.sqrt(model.cost_)
        labels.append(label)
        values.append(e)

idx = pandas.MultiIndex.from_tuples(labels, names=['fit_type', 'metric', 'story'])
err_df = pandas.DataFrame(values, index=idx, columns=['error'])
err_df = err_df.unstack(level=[0, 1])['error']
print('Avg. Error (%):')
print('===============')
print(err_df.mean().unstack(level=0).round().astype('int'))
print('Std. Err. (+/-)')
print('===============')
print(err_df.sem().unstack(level=0).round().astype('int'))
