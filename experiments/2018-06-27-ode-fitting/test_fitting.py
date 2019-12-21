import numpy
import scipy

from fitting import fitone
from models import hoaxmodel


def gendata(model, y0, t, sigma=0, *args):
    """
    Generate synthetic data with Gaussian noise from a given ODE model. The
    function uses `scipy.integrate.odeint` to integrate the ODE system from a
    given set of initial conditions, and then applies additional Gaussian noise
    with 0 mean and tunable sigma.

    Parameters
    ==========
    model : callable
        a function implementing an ODE system.

    y0 : ndarray
        the vector of initial conditions of the model.

    t : ndarray
        the vector time points at which to integrate the model.

    sigma : float
        variance of gaussian noise term (default is no noise).

    Notes
    =====
    Additional positional arguments (`args`) will be passed to `model` via
    odeint. This can be used to specify the actual parameters of the model.
    """
    y = scipy.integrate.odeint(model, y0, t, args=args)
    yerr = scipy.stats.norm.rvs(scale=sigma, size=y.shape)
    return numpy.c_[t, y + yerr]


def printparams(xopt, xerr=None, names=None):
    if names is None:
        names = [str(i) for i in range(len(xopt))]
    tw = max(map(len, names))
    names = [n.rjust(tw) for n in names]
    if xerr is not None:
        for n, xo, xe in zip(names, xopt, xerr):
            print("{}: {:.2e} +/- {:.2e}".format(n, xo, xe))
    else:
        for n, xo in zip(names, xopt):
            print("{}: {:.2e}".format(n, xo))
    print()


if __name__ == '__main__':
    # Model parameters
    pv = 0.1
    tauinv = 0.1
    alpha = 0.5
    x = (pv, tauinv, alpha)

    # True value of the initial conditions of the system. In order they are:
    # BA0, FA0, BI0, FI0, S0
    y0 = (1000, 0, 0, 0, 9000)

    names = [
        "BA0",
        "FA0",
        "BI0",
        "FI0",
        "S0",
        "pv",
        "tauinv",
        "alpha"
    ]

    # The true parameter values
    printparams(y0 + x, names=names)

    # Vector of integration time steps
    t = numpy.linspace(0, 10, 11)

    # Generate data by integrating ODE system and applying Gaussian noise with
    # given sigma.
    sigma = 2
    data = gendata(hoaxmodel, y0, t, sigma, *x)

    # Keep only time, BA, FA
    data = data[:, :3]

    # Upper bound used by the optimiation routine for state variables unknowns
    N_max = 1e6

    # Scenario 1) The full vector of initial conditions is part of the unknown
    # parameters to fit. To achieve this, set `fity0=True`.

    bounds = [
        (0, N_max),  # BA0
        (0, N_max),  # FA0
        (0, N_max),  # BI0
        (0, N_max),  # FI0
        (0, N_max),  # S0
        (0, 1),  # pv
        (0, 1),  # tauinv
        (0, 1),  # alpha
    ]
    xopt1, err1 = fitone(data, hoaxmodel, 5, bounds, fity0=True, nrep=25)
    printparams(xopt1, err1, names)

    # Scenario 2) Only BI0/FI0/S0 are unknown parameters to fit; BA0/FA0 are
    # set to be equal to the first observation of the data.
    bounds = [
        (0, N_max),  # BI0
        (0, N_max),  # FI0
        (0, N_max),  # S0
        (0, 1),  # pv
        (0, 1),  # tauinv
        (0, 1),  # alpha
    ]
    xopt2, err2 = fitone(data, hoaxmodel, 5, bounds, nrep=25)
    printparams(xopt2, err2, names[2:])
