import numpy


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
    y = numpy.asfarray(y)
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


def odemodel(y, t, pv, tauinv, alpha):
    """
    The model expressed as a system of ordinary differential equations. Returns
    y'(t), the derivative at y(t). Can be simulated using numerical integration
    (see `scipy.integrate.odeint`).
    """
    _checkparams(pv, tauinv, alpha)
    y = numpy.asfarray(y)
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
    assert numpy.isclose(numpy.sum(dy), 0)
    return dy
