""" The SIR and the "double" SIR model """

import numpy


def sir(y, t, beta, mu):
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
    y = numpy.asfarray(y)
    S, I, R = y
    N = y.sum()
    dy = [
        - beta * I / N * S,  # S
        beta * I / N * S - mu * I,  # I
        mu * I  # R
    ]
    assert numpy.isclose(dy.sum(), 0), "sum(dy) is not zero"
    return dy


def doublesir(y, t, beta1, mu1, beta2, mu2):
    """
    Two independent SIR models

    See `sir`.
    """
    y = numpy.asfarray(y)
    S1, I1, R1, S2, I2, R2 = y
    dy1 = sir([S1, I1, R1], t, beta1, mu1)
    dy2 = sir([S2, I2, R2], t, beta2, mu2)
    dy = numpy.hstack([dy1, dy2])
    assert numpy.isclose(dy.sum(), 0), "sum(dy) is not zero"
    return dy
