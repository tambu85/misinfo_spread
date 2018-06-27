""" Compares simulation of probabilistic transition rates to model expressed as
a system of ordinary differential equations. """

from __future__ import print_function
import numpy
import matplotlib.pyplot as plt
import scipy.integrate

from models import probmodel, odemodel, simprobmodel


def compare(nsteps, y0, p):
    t = numpy.arange(nsteps)

    # Probabilistic model
    yprob = simprobmodel(nsteps, probmodel, y0, *p)

    # ODE model
    yrate = scipy.integrate.odeint(odemodel, y0, t, args=p, rtol=1e-8)

    ylabels = ["S", "BI", "BA", "FI", "FA"]
    labels = ['Prob.', 'ODE']
    fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(8, 5), sharex=True)
    for i, (ax, ylabel) in enumerate(zip(numpy.ravel(axs), ylabels)):
        plt.sca(ax)
        plt.plot(t, yprob[:, i], ls='-', c='gray', label=labels[0],
                 alpha=.75)
        plt.plot(t, yrate[:, i], 'k--', label=labels[1], alpha=.75)
        plt.xlabel('$t$')
        plt.ylabel(ylabel)

    plt.legend(loc='best')

    plt.sca(axs[1, 2])
    plt.plot(t, yprob.sum(axis=1), ls='-', c='gray', label=labels[0],
             alpha=.75)
    plt.plot(t, yrate.sum(axis=1), 'k--', label=labels[1], alpha=.75)
    plt.xlabel('$t$')
    plt.ylabel('S + BI + BA + FI + FA')

    plt.tight_layout()
    plt.show()
    return t, yprob, yrate


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('nsteps', type=int)
    parser.add_argument('pv', type=float)
    parser.add_argument('tauinv', type=float)
    parser.add_argument('alpha', type=float)
    parser.add_argument('S', type=float)
    parser.add_argument('BI', type=float)
    parser.add_argument('BA', type=float)
    parser.add_argument('FI', type=float)
    parser.add_argument('FA', type=float)
    args = parser.parse_args()
    p = (args.pv, args.tauinv, args.alpha)
    y0 = numpy.asfarray([args.S, args.BI, args.BA, args.FI, args.FA])
    compare(args.nsteps, y0, p)
