""" Hoax model by Tambuscio et al. """

import numpy

from models.base import BaseModel, Variable

__all__ = ['HoaxModel']

class HoaxModel(BaseModel):
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

    def __init__(self, pv, tauinv, alpha):
        super(HoaxModel, self).__init__()
        self.pv = pv
        self.tauinv = tauinv
        self.alpha = alpha

    @staticmethod
    def obs(y):
        """
        Returns BA and FA
        """
        return y[:, :2]

    def dy(self, y, t):
        # this assigns and checks that each variable is within its bounds
        self.y = numpy.asfarray(y)
        f = self.BA / self.y.sum()
        dy = [
            f * self.BI - (self.tauinv + self.pv) * self.BA,  # dBA
            f * self.FI - self.tauinv * self.FA,  # dFA
            self.alpha * f * self.S + self.tauinv * self.BA - (f + self.pv) * self.BI,  # dBI
            (1.0 - self.alpha) * f * self.S + self.pv * (self.BI + self.BA) + \
                self.tauinv * self.FA - f * self.FI,  # dFI
            -f * self.S,  # dS
        ]
        return dy
