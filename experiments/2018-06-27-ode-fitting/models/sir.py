""" The SIR and the "double" SIR model """

from models.base import ODEModel, Variable

__all__ = ['SIR', 'DoubleSIR']

# Number of steps of scipy.integrate.odeint
MXSTEP = 5_000


class SIR(ODEModel):
    """
    The SIR model

    State:
        S - susceptible
        I - infected
        R - recovered

    Transitions:
        S -> I
        I -> R

    Parameters:
        beta - infection rate
        mu - recovery rate
    """
    _theta = ["beta", "mu"]

    beta = Variable(lower=0)
    mu = Variable(lower=0)

    _y0 = ["S", "I", "R"]

    S = Variable(lower=0)
    I = Variable(lower=0)  # noqa
    R = Variable(lower=0)

    def dy(self, y, t):
        S, I, R = y
        N = float(y.sum())
        dS = - self.beta * I / N * S
        dI = self.beta * I / N * S - self.mu * I
        dR = self.mu * I
        dy = [dS, dI, dR]
        return dy


class DoubleSIR(ODEModel):
    """
    Two independent SIR models

    See `sir.SIR`.
    """
    _theta = ["beta1", "mu1", "beta2", "mu2"]

    beta1 = Variable(lower=0)
    mu1 = Variable(lower=0)
    beta2 = Variable(lower=0)
    mu2 = Variable(lower=0)

    _y0 = ["S1", "I1", "R1", "S2", "I2", "R2"]

    S1 = Variable(lower=0)
    I1 = Variable(lower=0)
    R1 = Variable(lower=0)
    S2 = Variable(lower=0)
    I2 = Variable(lower=0)
    R2 = Variable(lower=0)

    def __init__(self, **kwargs):
        super(DoubleSIR, self).__init__(**kwargs)
        kwargs1 = {}
        kwargs2 = {}
        for key in kwargs:
            if key.endswith("1"):
                kwargs1[key] = kwargs[key]
            elif key.endwith("2"):
                kwargs2[key] = kwargs[key]
            else:
                raise ValueError("Not a valid parameter: {}".format(key))
        self.sir1 = SIR(**kwargs1)
        self.sir2 = SIR(**kwargs2)

    @staticmethod
    def obs(y):
        """
        Returns I1 and I2
        """
        return y[:, [1, 4]]

    def simulate(self, times, full=False, **kwargs):
        _mxstep = kwargs.get('mxstep', 0)
        kwargs.update({'mxstep': max(MXSTEP, _mxstep)})
        return super(DoubleSIR, self).simulate(times, full=full, **kwargs)

    def _inity0_nonobs(self, I1, I2):
        self.I1 = I1
        self.I2 = I2
        self.sir1.I = I1  # noqa
        self.sir2.I = I2  # noqa

    def _inity0_none(self, I1, I2):
        self.I1 = I1
        self.I2 = I2
        self.sir1.I = I1  # noqa
        self.sir2.I = I2  # noqa
        self.R1 = 0
        self.R2 = 0
        self.sir1.R = 0
        self.sir2.R = 0
        # do not set S1/S2 --- they always have to be fit

    # XXX not sure how to make sure that N stays the same across the two models
    def dy(self, y, t):
        self.sir1.theta = self.theta[:2]
        self.sir2.theta = self.theta[2:]
        dy1 = self.sir1.dy(y[:3], t)
        dy2 = self.sir2.dy(y[3:], t)
        dy = dy1 + dy2  # list concatenation
        return dy
