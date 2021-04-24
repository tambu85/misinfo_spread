""" Hoax model with segregation by Tambuscio et al. """

from models.base import ODEModel, Variable

__all__ = ['SegHoaxModel']

# NOTE (Apr 24, 2021): pvgu is set to 0 in the __init__

# Number of steps of scipy.integrate.odeint
MXSTEP = 10_000


class SegHoaxModel(ODEModel):
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
        FA_gu  - active fact-checkers gullible
        BI_gu  - inactive believers gullible
        FI_gu  - inactive fact-checkers gullible
        S_gu   - susceptible gullible
        BA_sk  - active believers skeptic
        FA_sk  - active fact-checkers skeptic
        BI_sk  - inactive believers skeptic
        FI_sk  - inactive fact-checkers skeptic
        S_sk   - susceptible skeptic

    Parameters
    ==========
        pvgu    - probability to verify in the gullible group
        pvsk     - probability to verify in the skeptic group
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
    _theta = ["pvgu", "pvsk", "tauinv", "alpha", "seg", "gamma"]

    pvgu = Variable(lower=0, upper=1)
    pvsk = Variable(lower=0, upper=1)
    tauinv = Variable(lower=0, upper=1)
    alpha = Variable(lower=0, upper=1)
    seg = Variable(lower=0.5, upper=1)
    gamma = Variable(lower=0, upper=1)

    _y0 = [
        "BA_gu",
        "FA_gu",
        "BI_gu",
        "FI_gu",
        "S_gu",
        "BA_sk",
        "FA_sk",
        "BI_sk",
        "FI_sk",
        "S_sk"
    ]

    BA_gu = Variable(lower=0)
    FA_gu = Variable(lower=0)
    BI_gu = Variable(lower=0)
    FI_gu = Variable(lower=0)
    S_gu = Variable(lower=0)
    BA_sk = Variable(lower=0)
    FA_sk = Variable(lower=0)
    BI_sk = Variable(lower=0)
    FI_sk = Variable(lower=0)
    S_sk = Variable(lower=0)

    # Fix pvgu to 0
    def __init__(self, *args, **kwargs):
        super(SegHoaxModel, self).__init__(*args, **kwargs)
        self.pvgu = 0

    @staticmethod
    def obs(y):
        """
        Returns BA_gu + BA_sk and FA_gu + FA_sk
        """
        y_gu = y[:, :2]  # BA_gu, FA_gu
        y_sk = y[:, 5:7]  # BA_sk, FA_sk
        return y_gu + y_sk

    def simulate(self, times, full=False, **kwargs):
        _mxstep = kwargs.get('mxstep', 0)
        kwargs.update({'mxstep': max(MXSTEP, _mxstep)})
        return super(SegHoaxModel, self).simulate(times, full=full, **kwargs)

    def _inity0_none(self, BA, FA):
        # split fake fact
        self.BA_sk = 0.5 * BA
        self.FA_sk = 0.5 * FA
        self.BA_gu = 0.5 * BA
        self.FA_gu = 0.5 * FA
        # set to zero
        self.FI_sk = 0
        self.BI_sk = 0
        self.FI_gu = 0
        self.BI_gu = 0
        # do not set S_sk / S_gu -- they always have to be fit

    def _inity0_nonobs(self, BA, FA):
        # split fake fact
        self.BA_sk = 0.5 * BA
        self.FA_sk = 0.5 * FA
        self.BA_gu = 0.5 * BA
        self.FA_gu = 0.5 * FA

    def dy(self, y, t):
        BA_gu, FA_gu, BI_gu, FI_gu, S_gu, BA_sk, FA_sk, BI_sk, FI_sk, S_sk = y
        N = (BA_gu + BA_sk) / float(y.sum())
        fgu = self.seg * self.gamma * BA_gu / N + (1 - self.seg) * \
            (1 - self.gamma) * BA_sk / N
        fsk = self.seg * (1 - self.gamma) * BA_gu / N + (1 - self.seg) * \
            self.gamma * BA_sk / N
        dBA_gu = fgu * BI_gu - (self.tauinv + self.pvgu) * BA_gu
        dBA_sk = fsk * BI_sk - (self.tauinv + self.pvsk) * BA_sk
        dFA_gu = fgu * FI_gu - self.tauinv * FA_gu
        dFA_sk = fsk * FI_sk - self.tauinv * FA_sk
        dBI_gu = self.alpha * fgu * S_gu + self.tauinv * BA_gu - \
            (fgu + self.pvgu) * BI_gu
        dBI_sk = self.alpha * fsk * S_sk + self.tauinv * BA_sk - \
            (fsk + self.pvsk) * BI_sk
        dFI_gu = (1.0 - self.alpha) * fgu * S_gu + self.pvgu * \
            (BI_gu + BA_gu) + self.tauinv * FA_gu - fgu * FI_gu
        dFI_sk = (1.0 - self.alpha) * fsk * S_sk + self.pvsk * \
            (BI_sk + BA_sk) + self.tauinv * FA_sk - fsk * FI_sk
        dS_gu = -fgu * S_gu
        dS_sk = -fsk * S_sk
        dy = [
           dBA_gu, dFA_gu, dBI_gu, dFI_gu, dS_gu, dBA_sk, dFA_sk, dBI_sk,
           dFI_sk, dS_sk
        ]
        return dy
