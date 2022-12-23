""" Plot scatter matrix of parameters from pickle file with model fit results """

import matplotlib.pyplot as plt
import pandas
import pickle

from argparse import ArgumentParser

def plot_scatter_matrix(fn):
    obj = pickle.load(open(fn, 'rb'))
    k0 = list(obj['models'].keys())[0]
    m = obj['models'][k0]
    d = {k: v.gettheta() for k, v in obj['models'].items()}
    df = pandas.DataFrame.from_dict(d, orient='index')
    df.columns = m._theta
    axs = pandas.scatter_matrix(df)
    plt.show(block=False)
    return axs


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('file', help='pickle file with model fit results')
    args = parser.parse_args()
    plot_scatter_matrix(args.file)
