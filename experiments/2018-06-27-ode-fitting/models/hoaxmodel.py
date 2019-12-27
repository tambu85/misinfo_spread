""" Hoax model by Tambuscio et al. """

from models.base import ODEModel, Variable

__all__ = ['HoaxModel']

#  upper bound for all initial conditions. This is bigger than the total number
#  of daily active users of Twitter.
N_MAX = 1e5


class HoaxModel(ODEModel):
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
        pv      - probability to verify (bounded in [0,1])
        tauinv  - inverse tau (bounded in [0,1])
        alpha   - relative strenght of the hoax (bounded in [0, 1])

    Notes
    =====
    The model is expressed as a system of ordinary differential equations.
    Returns y'(t), the derivative at y(t). Can be simulated using numerical
    integration by calling the `simulate()` method:

    >>> from models.hoaxmodel import HoaxModel
    >>> m = HoaxModel(pv=.1, tauinv=.2, alpha=.3)
    >>> m.FA = m.BI = m.FI = 0
    >>> m.S = 9000
    >>> m.BA = 1000
    >>> m.simulate(times=list(range(10)))
    """
    _theta = ['pv', 'tauinv', 'alpha']

    pv = Variable(lower=0, upper=1)
    tauinv = Variable(lower=0, upper=1)
    alpha = Variable(lower=0, upper=1)

    _y0 = ['BA', 'FA', 'BI', 'FI', 'S']

    BA = Variable(lower=0, upper=N_MAX)
    FA = Variable(lower=0, upper=N_MAX)
    BI = Variable(lower=0, upper=N_MAX)
    FI = Variable(lower=0, upper=N_MAX)
    S = Variable(lower=0, upper=N_MAX)

    @staticmethod
    def obs(y):
        """
        Returns BA and FA
        """
        return y[:, :2]

    def dy(self, y, t):
        BA, FA, BI, FI, S = y
        f = BA / float(y.sum())
        dBA = f * BI - (self.tauinv + self.pv) * BA
        dFA = f * FI - self.tauinv * FA
        dBI = self.alpha * f * S + self.tauinv * BA - (f + self.pv) * BI
        dFI = (1.0 - self.alpha) * f * S + self.pv * (BI + BA) + \
            self.tauinv * FA - f * FI
        dS = -f * S
        dy = [dBA, dFA, dBI, dFI, dS]
        return dy
