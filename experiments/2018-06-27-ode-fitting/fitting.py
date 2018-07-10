""" Fitting script """

from __future__ import print_function

import numpy
import scipy.stats
import scipy.integrate
import scipy.optimize
# import argparse

# TODO perhaps remove y0base? Since x_scale seems to work fine.


def gendata(model, y0, t, sigma=0, *args):
    """
    model - ODE
    y0 - initial conditions
    t - time points
    sigma - variance of gaussian noise term
    obsvars - return only these variables (list of column indices)
    args - ODE model parameters
    """
    y = scipy.integrate.odeint(model, y0, t, args=args)
    yerr = scipy.stats.norm.rvs(scale=sigma, size=y.shape)
    return numpy.c_[t, y + yerr]


def _genresidualsfunc(func, data, n_vars, fity0=False, y0base=None,
                      aggfunc=None, i_obsvars=None, **kwargs):
    """
    Given a model and a 2D vector of empirical data, return a function that
    computes the residuals of the fit of the ODE model to the empirical data.

    Parameters
    ==========
    func : callable(y, t, ...)
        A function that computes the derivative of y at time t. This argument
        is passed to `scipy.integrate.odeint` for integration. y is a 1-D
        ndarray of size `n_vars`.

    data : ndarray
        A 2D array of size (N, M + 1) of observations. The first column
        corresponds to time values. The M remaining columns are observable
        variables. It must be `n_vars` >= M.

    n_vars : int
        Number of state variables of the model.

    fity0 : bool
        See `fitone`.

    y0base : float
        See `fitone`.

    aggfunc : callable(y)
        See `fitone`

    i_obsvars : list
        See `fitone`

    Additional keyword arguments are passed to `scipy.integrate.odeint`.

    Returns
    =======
    _fitresiduals : callable(x)
        Returns the residuals of the fit with parameter vector x. This
        functions is suitable for use with `scipy.optimize.least_squares`.
    """
    def _fitresiduals(x):
        if fity0:
            y0 = x[:n_vars]
            args = x[n_vars:]
        else:
            y0 = y[0]
            n = n_vars - len(y0)
            y0 = numpy.hstack([y0, x[:n]])
            args = x[n:]
        assert len(y0) == n_vars
        if y0base is not None:
            y0 = numpy.power(y0base, y0)
        yhat = scipy.integrate.odeint(func, y0, t, args=tuple(args), **kwargs)
        # aggregate result of the integration. Needed with the segregated
        # model.
        if aggfunc is not None:
            yhat = aggfunc(yhat)
        # select observable variables for residials
        if i_obsvars is not None:
            # user specified column indices
            assert len(i_obsvars) == n_obsvars, "Error: must match number "\
                "of data variables: {}".format(i_obsvars)
            yhat = yhat[:, i_obsvars]
        else:
            # by default use the fist n_obsvars
            yhat = yhat[:, :n_obsvars]
        yres = yhat - y
        return yres.ravel()
    if n_vars <= 0:
        raise ValueError('Error: n_vars must be > 0: {}'.format(n_vars))
    data = numpy.atleast_2d(data)
    t = data[:, 0]
    y = data[:, 1:]
    _, n_obsvars = y.shape
    if n_vars < n_obsvars:
        raise ValueError("Error: Not enough variables to fit (needs {}): "
                         "{}".format(n_obsvars, n_vars))
    return _fitresiduals


def fitone(data, modelfunc, n_vars, bounds, nrep=25, fity0=False,
           y0base=None, aggfunc=None, **kwargs):
    """
    Fit one dataset to an ODE model. Performs the fit by minimizing a loss
    function of the residuals between the model and the data.

    Parameters
    ==========

    data : ndarray
        A 2D array of shape (N, M + 1), where N is the number of observations.
        Each observations is of the form:
            (t, y_1(t), ..., y_M(t))
        where the first element is the time, and y_i(t) is the value of the
        i-th variable at time t.

    modelfunc : callable(y, t, ...)
        The ODE model. Computes the derivative of y at t. y can be an array of
        shape (M,).

    n_vars : int
        Number of state variables of the model

    bounds : list
        A list of pairs `(lower, upper)` specifying bounds for each parameter
        of the model.

    nrep : int
        Call `least_squares` multiple time sampling the starting conditions
        uniformly at random from the hypercube identified by `bounds` and pick
        the solution with the smallest error.

    fity0 : bool
        Optional; if True, estimate y0 as fit parameters. If False, take y0
        from the data. Default: False.

    y0base : int
        Optional; treat y0 as log-transformed in this base. To compute actual
        y0 needed to integrate, raise this base to the power of each exponent.
        The default is to not to use a log-transformation.

    aggfunc : callable(y)
        User-defined function that aggregates the integrated function before
        computing residuals.

    Additional keyword arguments will be passed to `scipy.integrate.odeint`.

    Returns
    =======
    xopt : ndarray
        Array of fitted parameter values.

    erropt : ndarray
        Standard errors of the fitted values
    """
    lower_bounds, upper_bounds = zip(*bounds)
    size = (nrep, len(bounds))
    x0arr = scipy.stats.uniform.rvs(lower_bounds, upper_bounds, size)
    x_scale = numpy.diff(bounds, axis=1).ravel()
    tmp = []
    for i in range(nrep):
        x0 = x0arr[i]
        _resid = _genresidualsfunc(modelfunc, data, n_vars, fity0=fity0,
                                   y0base=y0base, aggfunc=aggfunc, **kwargs)
        res = scipy.optimize.least_squares(_resid, x0, x_scale=x_scale,
                                           bounds=(lower_bounds, upper_bounds))
        tmp.append(res)
    best_res = min(tmp, key=lambda k: k.cost)
    return best_res.x, _stderr(best_res)


def _stderr(res):
    """
    Compute standard error of the fitted parameters
    """
    # Code adapted from: scipy.optimize.curve_fit
    # Do Moore-Penrose inverse discarding zero singular values.
    from scipy.linalg import svd
    _, s, VT = svd(res.jac, full_matrices=False)
    threshold = numpy.finfo(float).eps * max(res.jac.shape) * s[0]
    s = s[s > threshold]
    VT = VT[:s.size]
    pcov = numpy.dot(VT.T / s**2, VT)
    return 1.96 * numpy.sqrt(numpy.diag(pcov))


def relabserr(data, modelfunc, x):
    """
    Relative absolute error
    """
    t = data[:, 0]
    y = data[:, 1:]
    yh = modelfunc(y, t, x)
    e = numpy.ravel(numpy.abs((y - yh) / y)).sum() / data.size
    return e


def fitmany(datasets, modelfunc, n_vars, bounds, nrep=25, fity0=False,
            y0base=None, aggfunc=None, **kwargs):
    """
    Applies `fitone` to all data arrays in the `datasets`.

    Arguments
    =========

    datasets - sequence
        A list/sequence of data arrays (see `fitone`)

    ...
        See `fitone`

    Returns
    =======
    A list of results from `fitone`.

    """
    tmp = []
    for data in datasets:
        res = fitone(data, modelfunc, n_vars, bounds, nrep=nrep, fity0=fity0,
                     y0base=y0base, aggfunc=aggfunc, **kwargs)
        tmp.append(res)
    return tmp


if __name__ == '__main__':
    import models
    pv = 0.1
    tauinv = 0.1
    alpha = 0.5
    t = numpy.linspace(0, 10, 11)
    sigma = 2
    y0 = (1000, 0, 0, 0, 9000)
    data = gendata(models.hoaxmodel, y0, t, sigma, pv, tauinv, alpha)
    data = data[:, :3]

    N_max = 1e6

    # Fit all initial conditions
    bounds = [
        (0, N_max),  # BA
        (0, N_max),  # FA
        (0, N_max),  # BI
        (0, N_max),  # FI
        (0, N_max),  # S
        (0, 1),  # pv
        (0, 1),  # tauinv
        (0, 1),  # alpha
    ]
    xopt1 = fitone(data, models.hoaxmodel, 5, bounds, fity0=True)

    # Fit only non-observed initial conditions
    bounds = [
        (0, N_max),  # BI
        (0, N_max),  # FI
        (0, N_max),  # S
        (0, 1),  # pv
        (0, 1),  # tauinv
        (0, 1),  # alpha
    ]
    xopt2 = fitone(data, models.hoaxmodel, 5, bounds)

    numpy.set_printoptions(precision=2, suppress=True)
    print(numpy.round(xopt1, 2))
    print(numpy.round(xopt2, 2))
