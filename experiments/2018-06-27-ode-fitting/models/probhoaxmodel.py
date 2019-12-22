""" Hoax model with segregation by Tambuscio et al. (probabilistic version) """

import numpy

from hoaxmodel import _checkparams


def probmodel(y, t, pv, tauinv, alpha):
    """
    The model expressed as discrete probabilistic transitions. Returns state
    value at the next time step, y(t + 1). Can be simulated using the
    `simprobmodel` function.

    State:
        BA - active believers
        FA - active fact-checkers
        BI - inactive believers
        FI - inactive fact-checkers
        S - susceptible

    Parameters:
        pv - probability to verify
        tauinv - inverse tau
        alpha - relative strenght of the hoax
    """
    _checkparams(pv, tauinv, alpha)
    y = numpy.asfarray(y)
    FA, BA, BI, FI, S = y
    N = y.sum()
    f = BA / N
    y1 = [
        # FA (fact-checkers, active)
        f * FI + (1.0 - tauinv) * FA,
        # BA (believers, active)
        (1.0 - pv) * f * BI + (1.0 - tauinv) * (1.0 - pv) * BA,
        # BI (believers, inactive)
        alpha * f * S + tauinv * BA + (1.0 - pv) * (1.0 - f) * BI,
        # FI (fact-checkers, inactive)
        (1.0 - alpha) * f * S + tauinv * FA + pv * BI + pv * (1.0 - tauinv) \
        * BA + (1.0 - f) * FI,
        # S (susceptibles)
        (1.0 - f) * S,
    ]
    y1 = numpy.asfarray(y1)
    assert numpy.isclose(y1.sum(), N), "Number of agents changed"
    return y1


def simprobmodel(nsteps, f, y0, *args):
    """
    Simulate a probabilistic model by repeatedly applying the transition
    rules. This is currently used to perform all simulations and fits.
    """
    tmp = [y0]
    for i in range(nsteps - 1):
        y1 = f(y0, i, *args)
        tmp.append(y1)
        y0 = y1
    return numpy.asarray(tmp)
