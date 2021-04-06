""" Save fit results from pickles to CSV format """

import pickle
import argparse
import pandas

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("paths", nargs="+", help="Input pickles")
parser.add_argument("-o", "--output", help="Output CSV", default="output.csv")

if __name__ == '__main__':
    args = parser.parse_args()

    tmp = []
    print("Reading:")
    for path in args.paths:
        print(" - {}".format(path))
        obj = pickle.load(open(path, "rb"))
        modelcls = obj['modelcls']
        fity0 = obj['fity0']
        models = obj['models']
        d = {(k, modelcls, fity0): dict(zip(tuple(v._theta) + tuple(v._y0),
                                            tuple(v.theta) + tuple(v.y0))) 
             for k, v in models.items()}
        df = pandas.DataFrame.from_dict(d, orient='index')
        tmp.append(df)
    
    df = pandas.concat(tmp)
    df.index.names = ['storyid', 'modelcls', 'fity0']
    df.to_csv(args.output)
    print("Written: {}".format(args.output))
