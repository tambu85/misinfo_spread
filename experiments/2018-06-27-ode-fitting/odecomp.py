""" Compares simulation of probabilistic transition rates to model expressed as
a system of ordinary differential equations. """

from __future__ import print_function
import numpy
import matplotlib.pyplot as plt

from models import probmodel, simprobmodel, HoaxModel


def compare(nsteps, y0, p):
    t = numpy.arange(nsteps)

    # Probabilistic model
    yprob = simprobmodel(nsteps, probmodel, y0, *p)

    # ODE model
    hoaxmodel = HoaxModel()
    hoaxmodel.y0 = y0
    hoaxmodel.theta = p
    yrate = hoaxmodel.simulate(t, full=True)

    # Plotting
    ylabels = ["BA", "FA", "BI", "FI", "S"]
    labels = ['Prob.', 'ODE']
    fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(8, 5), sharex=True)
    for i, (ax, ylabel) in enumerate(zip(numpy.ravel(axs), ylabels)):
        plt.sca(ax)
        plt.plot(t, yprob[:, i], ls='-', c='gray', label=labels[0],
                 alpha=.75)
        plt.plot(t, yrate[:, i], 'k--', label=labels[1], alpha=.75)
        plt.xlabel('$t$')
        plt.ylabel(ylabel)


    # plot the total number of agents
    plt.sca(axs[1, 2])
    plt.plot(t, yprob.sum(axis=1), ls='-', c='gray', label=labels[0],
             alpha=.75)
    plt.plot(t, yrate.sum(axis=1), 'k--', label=labels[1], alpha=.75)
    plt.xlabel('$t$')
    plt.ylabel('BA + FA + BI + FI + S')
    plt.legend(loc='best')
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
    parser.add_argument('BA', type=float)
    parser.add_argument('FA', type=float)
    parser.add_argument('BI', type=float)
    parser.add_argument('FI', type=float)
    parser.add_argument('S', type=float)
    args = parser.parse_args()
    p = (args.pv, args.tauinv, args.alpha)
    y0 = numpy.asfarray([args.BA, args.FA, args.BI, args.FI, args.S])
    compare(args.nsteps, y0, p)
