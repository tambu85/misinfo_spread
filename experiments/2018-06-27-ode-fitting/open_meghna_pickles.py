import pandas
import os.path
import pickle

story_id_list = [3, 10, 13, 14, 18, 24, 25, 26, 27, 28, 29, 30, 31, 32, 36, 37, 44, 45, 46, 47]

basedir = "/home/giovanni/Desktop/Pickle models/"

d = {}

models = set()

for story_id in story_id_list:
    fn = "*{}.pkl".format(story_id)
    d[story_id] = {}
    path = os.path.join(basedir, fn)
    with open(path, 'rb') as f:
        count = pickle.load(f)
        for i in range(count):
            model = pickle.load(f)
            model_name = model.__class__.__name__
            models.add(model_name)
            d[story_id][model_name] = {}
            for name in model._theta:
                d[story_id][model_name][name] = getattr(model, name)

d2 = {}
df = pandas.DataFrame.from_dict(d, orient="index")

for model_name in models:
    d_model = df[model_name].to_dict()
    df_model = pandas.DataFrame.from_dict(d_model, orient="index")
    d2[model_name] = df_model
