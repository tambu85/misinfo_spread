# TODO List

Legend:
```
- [X] Task       = done
- [X] ~~Task~~   = won't fix / not needed anymore
```

## High priority:
- [X] Run fit with --fity0=non-obs on HoaxModel;
- [X] Run fit with --fity0=all on HoaxModel;
- [X] Run fit with --fity0=none on HoaxModel;
- [X] Compare results of fity0 alternatives and decide what is best option;
- [X] Investigate odeint instabilities on SegHoaxModel, DoubleSIR, SEIZ (fit synth data);
- [X] Run fit for all models (fity0 = all);
- [X] Compare MAPE/SMAPE/LOG ACC RATIO/RMSE for model selection;
- [X] Do not set S to zero in fity0 = none;
- [X] Re-run `test_fitting.py` on HoaxModel;
- [X] Run fit for all models (fity0 = non-obs);
- [X] Recompute errors;
- [ ] Remove cumsum() call from curves.py;
- [ ] Refresh data;
- [ ] Run fit with --fity0=non-obs;
- [ ] Run fit with --fity0=all;
- [ ] Update all fit results on presentation;
- [ ] Check for numerical integration errors of SegHoaxModel fit (if any); 
- [ ] Plot all fits using panel plot;

## Normal priority: 
- [ ] Write k-means + PCA script for model-based clustering;
- [ ] Forecast y(t) (for t=12h,24h,48h,168h) with variable-size training set;
- [ ] Repeat fit on the full dataset;

## Low priority:
- [ ] Repeat fit on number of tweets instead of number of users;
- [ ] Fix issue with `ODEModel.summary` (see FIXME in `models/base.py`)
- [ ] Fix issue with root logger (see FIXME in `fit.py`);
- [X] Fix issue with `utils.logaccratio`
- [ ] Fix issue with missing data folder for package (see FIXME in `fit.py`).
- [ ] Move ode-fitting code under replication;
- [ ] Write Snakefile(s) for replication;
- [ ] Create minimal environment for replication;
- [X] ~~Test `scipy.integrate.solve_ivp` as replacement for `odeint`;~~
- [ ] Implement more models from literature (see in `models.__init__.py`);
- [ ] Write test cases for models.base.Variable, models.base.ODEModel;
- [ ] Write test cases for odeint based on `test_fitting.py` (fit synthetic data);
- [ ] Make test case based on `odecomp.py` (compare odeint with prob updating);
- [X] ~~Implement Jacobian using SymPy to speed up least squares fitting;~~
- [ ] Refactor `models.base.ODEModel` based on [scikit-learn API](https://scikit-learn.org/stable/developers/develop.html);
