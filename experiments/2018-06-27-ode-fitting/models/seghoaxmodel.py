""" Hoax model with segregation by Tambuscio et al. """

import numpy


def _checkparamsseg(pv, tauinv, alphagu, alphask, s, gamma):
    assert 0 <= pv <= 1, "pv: out of bounds: {}".format(pv)
    assert 0 <= alphagu <= 1, "alphagu: out of bounds: {}".format(alphagu)
    assert 0 <= alphask <= 1, "alphask: out of bounds: {}".format(alphask)
    assert 0 <= tauinv <= 1, "tauinv: out of bounds: {}".format(tauinv)
    assert 0.5 <= s <= 1, "s: out of bounds: {}".format(s)
    assert 0 <= gamma <= 1, "gamma: out of bounds: {}".format(gamma)


def hoaxmodelseg_aggfunc(y):
    return numpy.reshape(y, (-1, 2)).sum(axis=1)


def hoaxmodelseg(y, t, pvgu, pvsk, tauinv, alpha, s, gamma):
    """
    Hoax Model by Tambuscio et al. This is the model with segregation.

    Transitions
    ===========
        S_i -> BI_i <-> BA_i
        S_i -> FI_i <-> FA_i
        BI_i -> FI_i
        BA_i -> FI_i

    i = {sk, gu}

    State
    =====
        S_gu   - susceptible gullible
        S_sk   - susceptible skeptic
        BI_gu  - inactive believers gullible
        BI_sk  - inactive believers skeptic
        BA_gu  - active believers gullible
        BA_sk  - active believers skeptic
        FI_gu  - inactive fact-checkers gullible
        FI_sk  - inactive fact-checkers skeptic
        FA_gu  - active fact-checkers gullible
        FA_sk  - active fact-checkers skeptic

    Parameters
    ==========
        pvgu    - probability to verify in the gullible group
        psk     - probability to verify in the skeptic group
        tauinv  - inverse tau
        alpha   - relative strenght of the hoax
        s       - network segregation
        gamma   - relative size of the gullible group

    Notes
    =====
    The model is expressed as a system of ordinary differential equations.
    Returns y'(t), the derivative at y(t). Can be simulated using numerical
    integration (see `scipy.integrate.odeint`).

    """
    _checkparamsseg(pvgu, pvsk, tauinv, alpha, s, gamma)
    y = numpy.asfarray(y)
    BAgu, BAsk, FAgu, FAsk, BIgu, BIsk,  FIgu, FIsk, Sgu, Ssk, = y
    N = y.sum()
    fgu = s * gamma * BAgu / N + (1 - s) * (1 - gamma) * BAsk / N
    fsk = s * (1 - gamma) * BAgu / N + (1 - s) * gamma * BAsk / N
    dy = [
        fgu * BIgu - (tauinv + pvgu) * BAgu,  # BAgu
        fsk * BIsk - (tauinv + pvsk) * BAsk,  # BAsk
        fgu * FIgu - tauinv * FAgu,  # FAgu
        fsk * FIsk - tauinv * FAsk,  # FAsk
        alpha * fgu * Sgu + tauinv * BAgu - (fgu + pvgu) * BIgu,  # BIgu
        alpha * fsk * Ssk + tauinv * BAsk - (fsk + pvsk) * BIsk,  # BIsk
        (1.0 - alpha) * fgu * Sgu + pvgu * (BIgu + BAgu) + tauinv * FAgu - \
        fgu * FIgu,  # FIgu
        (1.0 - alpha) * fsk * Ssk + pvsk * (BIsk + BAsk) + tauinv * FAsk - \
        fsk * FIsk,  # FIsk
        -fgu * Sgu,  # Sgu
        -fsk * Ssk,  # Ssk
    ]
    assert numpy.isclose(numpy.sum(dy), 0), "sum(dy) does not cancel out"
    return dy
