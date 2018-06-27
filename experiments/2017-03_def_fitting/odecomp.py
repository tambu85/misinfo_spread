""" Compares simulation of probabilistic transition rates to model expressed as
a system of ordinary differential equations. """

from __future__ import print_function
import numpy
import matplotlib.pyplot as plt
import scipy.integrate

# TODO
# - rewrite Diego's function that returns the solution of the system using
#   Euler's method. It should return all values.
# - write the alternative implementation using odeint (Runge-Kutta)
# - compute the error defined as the total number of agents minus the given
#   error
# - compare the errors over different values of pv, tauinv, and alpha


def _checkparams(pv, tauinv, alpha):
    assert 0 <= pv <= 1, "pv: out of bounds: {}".format(pv)
    assert 0 <= alpha <= 1, "alpha: out of bounds: {}".format(alpha)
    assert 0 <= tauinv <= 1, "tauinv: out of bounds: {}".format(tauinv)


def probmodel(y, t, pv, tauinv, alpha):
    """
    The model expressed as discrete probabilistic transitions. Returns the
    value at the next time step, y(t + 1).
    """
    _checkparams(pv, tauinv, alpha)
    y = numpy.asarray(y)
    S, BI, BA, FI, FA = y
    N = y.sum()
    f = BA / N
    dy = [
        # S (susceptibles)
        (1.0 - f) * S,
        # BI (believers, inactive)
        alpha * f * S + tauinv * BA + (1.0 - pv) * (1.0 - f) * BI,
        # BA (believers, active)
        (1.0 - pv) * f * BI + (1.0 - tauinv) * (1.0 - pv) * BA,
        # FI (fact-checkers, inactive)
        (1.0 - alpha) * f * S + tauinv * FA + pv * BI + pv * (1.0 - tauinv) \
        * BA + (1.0 - f) * FI,
        # FA (fact-checkers, active)
        f * FI + (1.0 - tauinv) * FA
    ]
    return dy


def simprob(nsteps, f, y0, *args):
    """
    Simulate the probabilistic model by repeatedly applying the transition
    rules. This is currently used to perform all simulations and fits.
    """
    tmp = [numpy.hstack([0, y0])]
    for i in range(1, nsteps + 1):
        y1 = f(y0, i, *args)
        tmp.append(numpy.hstack([i, y1]))
        y0 = y1
    return numpy.asarray(tmp)


def ratemodel(y, t, pv, tauinv, alpha):
    """
    The model expressed as continuous rates. Returns y'(t), the derivative at
    y(t). Can be simulated using numerical integration (see
    `scipy.integrate.odeint`).
    """
    _checkparams(pv, tauinv, alpha)
    y = numpy.asarray(y)
    S, BI, BA, FI, FA = y
    N = y.sum()
    f = BA / N
    dy = [
        -f * S,  # S
        alpha * f * S + tauinv * BA - (f + pv) * BI,  # BI
        f * BI - (tauinv + pv) * BA,  # BA
        (1.0 - alpha) * f * S + pv * (BI + BA) + tauinv * FA - f * FI,  # FI
        f * FI - tauinv * FA  # FA
    ]
    return dy


p = (
    5e-3,  # pv
    1e-3,  # tauinv
    8e-1,  # alpha
)
y0 = numpy.asarray([0.98, 0.0, 0.02, 0.0, 0.0]) * 10000
nsteps = 100

# Discrete model
yprob = simprob(nsteps, probmodel, y0, *p)

# Continuous model
t = numpy.linspace(0, nsteps, nsteps + 1)
yrate = scipy.integrate.odeint(ratemodel, y0, t, args=p)
yrate = numpy.c_[t, yrate]

ylabels = ["S", "BI", "BA", "FI", "FA"]
labels = ['Prob.', 'Rate']
fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(8, 5), sharex=True)
for i, (ax, ylabel) in enumerate(zip(numpy.ravel(axs), ylabels)):
    plt.sca(ax)
    plt.plot(t, yprob[:, i + 1], ls='-', c='gray', label=labels[0], alpha=.75)
    plt.plot(t, yrate[:, i + 1], 'k--', label=labels[1], alpha=.75)
    plt.ylabel(ylabel)

plt.legend(loc='best')

for ax in [axs[1, 0], axs[1, 1], axs[0, 2]]:
    ax.set_xlabel("$t$")

fig.delaxes(axs[-1, -1])
plt.tight_layout()
plt.show()
