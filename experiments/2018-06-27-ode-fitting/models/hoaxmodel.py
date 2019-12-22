""" Hoax model by Tambuscio et al. """

import numpy


def _checkparams(pv, tauinv, alpha):
    assert 0 <= pv <= 1, "pv: out of bounds: {}".format(pv)
    assert 0 <= alpha <= 1, "alpha: out of bounds: {}".format(alpha)
    assert 0 <= tauinv <= 1, "tauinv: out of bounds: {}".format(tauinv)


def hoaxmodel(y, t, pv, tauinv, alpha):
    """
    Hoax Model by Tambuscio et al. This is the model without segregation.

    Transitions
    ===========
        S -> BI <-> BA
        S -> FI <-> FA
        BI -> FI
        BA -> FI

    State
    =====
        BA  - active believers
        FA  - active fact-checkers
        BI  - inactive believers
        FI  - inactive fact-checkers
        S   - susceptible

    Parameters
    ==========
        pv      - probability to verify
        tauinv  - inverse tau
        alpha   - relative strenght of the hoax

    Notes
    =====
    The model is expressed as a system of ordinary differential equations.
    Returns y'(t), the derivative at y(t). Can be simulated using numerical
    integration (see `scipy.integrate.odeint`).

    """
    _checkparams(pv, tauinv, alpha)
    y = numpy.asfarray(y)
    FA, BA, BI, FI, S = y
    N = y.sum()
    f = BA / N
    dy = [
        f * FI - tauinv * FA,  # FA
        f * BI - (tauinv + pv) * BA,  # BA
        alpha * f * S + tauinv * BA - (f + pv) * BI,  # BI
        (1.0 - alpha) * f * S + pv * (BI + BA) + tauinv * FA - f * FI,  # FI
        -f * S,  # S
    ]
    assert numpy.isclose(numpy.sum(dy), 0), "sum(dy) does not cancel out"
    return dy
