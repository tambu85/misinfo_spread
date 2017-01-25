#!/usr/bin/env python

import scipy, scipy.integrate

# Parameters
beta = 0.5
rho = 0.3
epsilon = 0.1
b = 0.1
p = 0.1
l = 0.1


S0 = 0.4
E0 = 0.3
I0 = 0.0
Z0 = 0.3


Y0 = [ S0, E0, I0, Z0 ]
tMax = 100

T = scipy.linspace(0, tMax, 101)
def rhs(Y, t, rho, l, b, beta, p, epsilon):

    S = Y[0]
    E = Y[1]
    I = Y[2]
    Z = Y[3]

    N = S + E + I + Z

    dS = - beta * I * S / N - b * Z * S / N
    dE = (1-p) * beta * I * S / N + (1-l) * b * Z * S / N - rho * E * I / N - epsilon * E
    dI = p * beta * I * S / N + (1-l) * b * Z * S / N - rho * E * I / N + epsilon * E
    dZ = l * b * S * Z / N

    dY = [ dS, dE, dI, dZ]

    return dY

solution = scipy.integrate.odeint(rhs,
                                  Y0,
                                  T,
                                  args = (rho, l, b, beta, p, epsilon))

S = solution[:, 0]
E = solution[:, 1]
I = solution[:, 2]
Z = solution[:, 3]

N = S + E + I + Z


import pylab


pylab.figure()

pylab.plot(T, S / N,
           T, E / N,
           T, I / N,
           T, Z / N)

pylab.xlabel('Time')
pylab.ylabel('Proportion')

pylab.legend([ 'Susceptible', 'Exposed', 'Infective', 'Skeptic' ])

pylab.show()
