""" Hoax model by Tambuscio et al. """

import numpy

from models.base import ODEModel, Variable

__all__ = ['HoaxModel']

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
        pv      - probability to verify \in [0,1]
        tauinv  - inverse tau \in [0,1]
        alpha   - relative strenght of the hoax \in [0, 1]

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

    _y = ['BA', 'FA', 'BI', 'FI', 'S']

    BA = Variable(lower=0)
    FA = Variable(lower=0)
    BI = Variable(lower=0)
    FI = Variable(lower=0)
    S = Variable(lower=0)

    @staticmethod
    def obs(y):
        """
        Returns BA and FA
        """
        return y[:, :2]

    def dy(self, y, t):
        self.y = numpy.asfarray(y)
        f = self.BA / self.y.sum()
        dBA = f * self.BI - (self.tauinv + self.pv) * self.BA
        dFA = f * self.FI - self.tauinv * self.FA
        dBI = self.alpha * f * self.S + self.tauinv * self.BA - (f + self.pv) * self.BI
        dFI = (1.0 - self.alpha) * f * self.S + self.pv * (self.BI + self.BA) + \
            self.tauinv * self.FA - f * self.FI
        dS = -f * self.S  # dS
        dy = [dBA, dFA, dBI, dFI, dS]
        return dy
