import numpy
import scipy

from fitting import fitone
from models import hoaxmodel


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


if __name__ == '__main__':
    pv = 0.1
    tauinv = 0.1
    alpha = 0.5
    t = numpy.linspace(0, 10, 11)
    sigma = 2
    y0 = (1000, 0, 0, 0, 9000)
    data = gendata(hoaxmodel, y0, t, sigma, pv, tauinv, alpha)
    data = data[:, :3]

    N_max = 1e6

    # All initial conditions are unknown parameters to fit
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
    xopt1, err1 = fitone(data, hoaxmodel, 5, bounds, fity0=True, nrep=1)

    # Only BI/FI/S are unknown parameters to fit, but no BA/FA
    bounds = [
        (0, N_max),  # BI
        (0, N_max),  # FI
        (0, N_max),  # S
        (0, 1),  # pv
        (0, 1),  # tauinv
        (0, 1),  # alpha
    ]
    xopt2, err2 = fitone(data, hoaxmodel, 5, bounds, nrep=1)

    numpy.set_printoptions(precision=2, suppress=True)
    print("{} +/- {}".format(numpy.round(xopt1, 2), numpy.round(err1, 2)))
    print("{} +/- {}".format(numpy.round(xopt2, 2), numpy.round(err2, 2)))
