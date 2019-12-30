# TODO List

## High priority:
[ ] Fit all models on simplified dataset;
[ ] Fit all models on full dataset;
[ ] Plot MAPE/SMAPE/LOG ACC RATIO/RMSE to do model selection;
[ ] Fit with --fity0=all and compared to results with default method;
[ ] Write k-means + PCA script for model-based clustering;
[ ] Do forecasting with 80-20 holdout set;

## Normal priority: 
[ ] Create minimal environment for replication;
[ ] Move ode-fitting experiment under replication;
[ ] Create Snakemake file for replication;

## Low priority:
[ ] Implement more models from literature (see in `models.__init__.py`);
[ ] Test cases for models.base.Variable, models.base.ODEModel;
[ ] Generic test case for all models based on same idea of `test_fitting.py`;
[ ] Make test case with `odecomp.py`;
[ ] Implement Jacobian using SymPy to speed up least squares fitting;
