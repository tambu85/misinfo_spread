""" SEIZ model by et al. Jin et al. (2013) """

from models.base import ODEModel, Variable

__all__ = ['SEIZ']


class SEIZ(ODEModel):
    """
    SEIZ model from "Epidemiological Modeling of News and Rumors on Twitter",
    by Jin et al. (2013), Proc. SNA-KDD'13.

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
    rho     - E -> I contact rate
    l       - S -> Z conditional probability on Z
    b       - S -> Z contact rate
    beta    - S -> I contact rate
    p       - S -> I conditional probability on I
    epsilon - Incubation rate
    """
    _theta = ["rho", "l", "b", "beta", "p", "epsilon"]

    rho = Variable(lower=0, upper=1)  # XXX upper?
    l = Variable(lower=0, upper=1)  # noqa
    b = Variable(lower=0, upper=1)  # XXX upper?
    beta = Variable(lower=0, upper=1)  # XXX upper?
    p = Variable(lower=0, upper=1)  # XXX upper?
    epsilon = Variable(lower=0, upper=1)  # XXX upper?

    _y0 = ["S", "E", "I", "Z"]

    S = Variable(lower=0)
    E = Variable(lower=0)
    I = Variable(lower=0)  # noqa
    Z = Variable(lower=0)

    @staticmethod
    def obs(y):
        """
        Return I and Z
        """
        return y[:, 2:]

    def dy(self, y, t):
        S, E, I, Z = y
        N = float(y.sum())
        dS = - self.beta * I * S / N - self.b * Z * S / N
        dE = (1.0 - self.p) * self.beta * I * S / N + (1.0 - self.l) * \
            self.b * Z * S / N - self.rho * E * I / N - self.epsilon * E
        dI = self.p * self.beta * I * S / N + (1.0 - self.l) * \
            self.b * Z * S / N - self.rho * E * I / N + self.epsilon * E
        dZ = self.l * self.b * S * Z / N
        dy = [dS, dE, dI, dZ]
        return dy
