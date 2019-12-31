# TODO List

## High priority:
- [X] Run fit with --fity0=non-obs on HoaxModel;
- [X] Run fit with --fity0=all on HoaxModel;
- [X] Run fit with --fity0=none on HoaxModel;
- [ ] Compare results of fity0 alternatives and decide what is best option;
- [ ] Investigate odeint instabilities on SegHoaxModel, DoubleSIR, SEIZ (fit synth data);
- [ ] Run fit for all models on simplified dataset;
- [ ] Plot MAPE/SMAPE/LOG ACC RATIO/RMSE to do model selection;

## Normal priority: 
- [ ] Write k-means + PCA script for model-based clustering;
- [ ] Do forecasting with 80-20 holdout set;
- [ ] Repeat fit on full dataset;
- [ ] Create minimal environment for replication;
- [ ] Move ode-fitting code under replication;
- [ ] Create master Snakemake file for replication;

## Low priority:
- [ ] Test `scipy.integrate.solve_ivp` as replacement for `odeint`;
- [ ] Implement more models from literature (see in `models.__init__.py`);
- [ ] Write test cases for models.base.Variable, models.base.ODEModel;
- [ ] Write test cases for odeint based on `test_fitting.py` (fit synthetic data);
- [ ] Make test case based on `odecomp.py` (compare odeint with prob updating);
- [ ] Implement Jacobian using SymPy to speed up least squares fitting;
- [ ] Refactor `models.base.ODEModel` based on [scikit-learn API](https://scikit-learn.org/stable/developers/develop.html)
