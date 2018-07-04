import numpy

# TODO write ODE for the following deterministic models
# 1. [DONE] The "segregated" model.
# 2. The normal SIR (I = believers, R = fact-checkers)
# 3. Double independent SIR (I1 = believers, I2 = fact-checkers)
# 4. [DONE] The SEIZ model by Jin et al. (Virginia Tech)
# 5. The model by Bettencourt et al.
# 6. The DK model by Daley and Kendall (see review by Vespignani et al.)
# 7. The MT model by Maki and Thompson
# 8. The model by Nekovee et al. ("Theory of rumor spreading in complex social
# networks")
# 9. The "Higgs rumor" model by Yamir Moreno and Sandro Meloni(?).


# -----------------------------------------------------------------------------
# Hoax model by Tambuscio et al.
# -----------------------------------------------------------------------------

def _checkparams(pv, tauinv, alpha):
    assert 0 <= pv <= 1, "pv: out of bounds: {}".format(pv)
    assert 0 <= alpha <= 1, "alpha: out of bounds: {}".format(alpha)
    assert 0 <= tauinv <= 1, "tauinv: out of bounds: {}".format(tauinv)


hoaxmodel_bounds = [
    (0, 1),  # pv
    (0, 1),  # tauinv
    (0, 1),  # alpha
]


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
    BA, FA, BI, FI, S = y
    N = y.sum()
    f = BA / N
    dy = [
        f * BI - (tauinv + pv) * BA,  # BA
        f * FI - tauinv * FA,  # FA
        alpha * f * S + tauinv * BA - (f + pv) * BI,  # BI
        (1.0 - alpha) * f * S + pv * (BI + BA) + tauinv * FA - f * FI,  # FI
        -f * S,  # S
    ]
    assert numpy.isclose(numpy.sum(dy), 0), "sum(dy) does not cancel out"
    return dy

# -----------------------------------------------------------------------------
# Hoax model with segregation by Tambuscio et al.
# -----------------------------------------------------------------------------


def _checkparamsseg(pv, tauinv, alphagu, alphask, s, gamma):
    assert 0 <= pv <= 1, "pv: out of bounds: {}".format(pv)
    assert 0 <= alphagu <= 1, "alphagu: out of bounds: {}".format(alphagu)
    assert 0 <= alphask <= 1, "alphask: out of bounds: {}".format(alphask)
    assert 0 <= tauinv <= 1, "tauinv: out of bounds: {}".format(tauinv)
    assert 0 <= s <= 1, "s: out of bounds: {}".format(s)
    assert 0 <= gamma <= 1, "gamma: out of bounds: {}".format(gamma)


hoaxmodelseg_bounds = [
    (0, 1),  # pv
    (0, 1),  # alphagu
    (0, 1),  # alphask
    (0, 1),  # tauinv
    (0, 1),  # s
    (0, 1),  # gamma
]


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
        BA_gu  - active believers gullible
        BA_sk  - active believers skeptic
        FA_gu  - active fact-checkers gullible
        FA_sk  - active fact-checkers skeptic
        BI_gu  - inactive believers gullible
        BI_sk  - inactive believers skeptic
        FI_gu  - inactive fact-checkers gullible
        FI_sk  - inactive fact-checkers skeptic
        S_gu   - susceptible gullible
        S_sk   - susceptible skeptic

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
    BAgu, BAsk, FAgu, FAsk, BIgu, BIsk, FIgu, FIsk, Sgu, Ssk = y
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


# -----------------------------------------------------------------------------
# SEIZ model by et al. Jin et al. (2013)
# -----------------------------------------------------------------------------

def seiz(Y, t, rho, l, b, beta, p, epsilon):
    """
    SEIZ model from "Epidemiological of News and Rumors on Twitter", by Jin et
    al. (2013), Proc. SNA-KDD'13.

    Transitions
    ===========
    S -> I
    S -> Z
    S -> E
    E -> I

    State
    =====
    S - Susceptible
    E - Exposed
    I - Infective
    Z - Skeptic

    Parameters
    ==========
    pho     - E -> I contact rate
    l       - S -> Z conditional probability on Z
    b       - S -> Z contact rate
    beta    - S -> I contact rate
    p       - S -> I conditional probability on I
    epsilon - Incubation rate
    """
    Y = numpy.asfarray(Y)
    S = Y[0]
    E = Y[1]
    I = Y[2]  # noqa
    Z = Y[3]
    N = S + E + I + Z
    dS = - beta * I * S / N - b * Z * S / N
    dE = (1-p) * beta * I * S / N + (1-l) * b * Z * S / N - rho * E * I / N -\
        epsilon * E
    dI = p * beta * I * S / N + (1-l) * b * Z * S / N - rho * E * I / N + \
        epsilon * E
    dZ = l * b * S * Z / N
    dY = numpy.asarray([dS, dE, dI, dZ])
    assert numpy.isclose(numpy.sum(dY), 0), "sum(dY) does not cancel out"
    return dY


# TODO must choose bounds for rates (pho, b, beta), cannot just set them to 1
seiz_bounds = [
    (0, 1),  # pho
    (0, 1),  # l
    (0, 1),  # b
    (0, 1),  # beta
    (0, 1),  # p
    (0, 1),  # epsilon
]


# -----------------------------------------------------------------------------
# Other functions
# -----------------------------------------------------------------------------

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
    BA, FA, BI, FI, S = y
    N = y.sum()
    f = BA / N
    y1 = [
        # BA (believers, active)
        (1.0 - pv) * f * BI + (1.0 - tauinv) * (1.0 - pv) * BA,
        # FA (fact-checkers, active)
        f * FI + (1.0 - tauinv) * FA,
        # BI (believers, inactive)
        alpha * f * S + tauinv * BA + (1.0 - pv) * (1.0 - f) * BI,
        # FI (fact-checkers, inactive)
        (1.0 - alpha) * f * S + tauinv * FA + pv * BI + pv * (1.0 - tauinv) \
        * BA + (1.0 - f) * FI,
        # S (susceptibles)
        (1.0 - f) * S,
    ]
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
