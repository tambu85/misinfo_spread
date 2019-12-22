""" SEIZ model by et al. Jin et al. (2013) """

import numpy


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
