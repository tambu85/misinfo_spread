import numpy

# TODO write ODE for the following deterministic models
# 1. The "segregated" model.
# 2. Double SIR.
# 3. The SEIZ model by Yamir Moreno and Sandro Meloni(?).
# 4. The model by the Virginia Tech people.
# 5. The model by Bettencourt et al.
# 6. The rumor model by Daley et al. (see review by Vespignani et al.)


#-------------------------------------------------------------------------------
# Tambuscio et al.
#-------------------------------------------------------------------------------

def _checkparams(pv, tauinv, alpha):
    assert 0 <= pv <= 1, "pv: out of bounds: {}".format(pv)
    assert 0 <= alpha <= 1, "alpha: out of bounds: {}".format(alpha)
    assert 0 <= tauinv <= 1, "tauinv: out of bounds: {}".format(tauinv)


def hoaxmodel(y, t, pv, tauinv, alpha):
    """
    Hoax Model by Tambuscio et al.

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


#-------------------------------------------------------------------------------
# Other functions
#-------------------------------------------------------------------------------

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

