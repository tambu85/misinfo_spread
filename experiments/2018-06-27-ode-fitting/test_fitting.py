import numpy
import scipy
import matplotlib.pyplot as plt

from models.hoaxmodel import HoaxModel


def printparams(xopt, xerr=None, names=None):
    if names is None:
        names = [str(i) for i in range(len(xopt))]
    tw = max(map(len, names))
    names = [n.rjust(tw) for n in names]
    if xerr is not None:
        for n, xo, xe in zip(names, xopt, xerr):
            print("{}: {:.2e} +/- {:.2e}".format(n, xo, xe))
    else:
        for n, xo in zip(names, xopt):
            print("{}: {:.2e}".format(n, xo))
    print()


def plot(fig, model, times, data=None, **kwargs):
    fig = plt.gcf()
    axs = fig.axes
    y = model.simulate(times)
    M = y.shape[1]
    titles = ['BA', 'FA']
    for k in range(M):
        axs[k].set_title(titles[k])
        axs[k].plot(times, y[:, k], **kwargs)
        if data is not None:
            axs[k].plot(times, data[:, k], color='k', ls='', marker='o',
                        label='data')
    axs[0].legend()


if __name__ == '__main__':
    # For reproducibility. Change seed to get different random numbers.
    numpy.random.seed(214)

    # Model parameters
    m = HoaxModel(pv=0.1, tauinv=0.01, alpha=0.5)

    m.FA = m.FI = m.BI = 0
    m.S = 9000
    m.BA = 1000

    # The true parameter values
    printparams(m.theta, names=m._theta)
    printparams(m.y0, names=m._y0)

    # Vector of integration time steps
    tmax = 168
    t = numpy.arange(tmax)

    # Generate data by simulating the ODE and applying Gaussian noise with
    # given sigma.
    sigma = 50
    y = m.simulate(t)
    yerr = scipy.stats.norm.rvs(scale=sigma, size=y.shape)

    # Add a fraction of outliers to simulate noisy tweet counts.
    p_outliers = 0.1
    n_outliers = int(len(t) * p_outliers)
    idx = numpy.random.choice(len(t), n_outliers, replace=False)
    yerr[idx] *= 10

    # Add noise to simulated data. Finally, clip negative values to zero, to
    # simulate count data.
    data = y + yerr
    data = data.clip(min=0)

    # Scenario 1) Fit unknowns = model parameter (theta) + initial conditions
    # (y0). All fits are best of three (3) attempts.
    m1 = HoaxModel()
    m1.fit(data, nrep=3)

    # Scenario 2) Like 1), but only BI0/FI0/S0 are unknown initial conditions.
    # BA0/FA0 are known and they are equal to the first observation of the
    # data.
    m2 = HoaxModel()
    m2.BA, m2.FA = data[0]
    m2.fit(data, nrep=3)

    # Plot true model, data, and fitted models.
    fig, axs = plt.subplots(1, 2)
    plot(fig, m, t, data, label='True', ls='-', lw=2)
    plot(fig, m1, t, label='Fit #1 (all unknowns)', ls='--')
    plot(fig, m2, t, label='Fit #2 (BA0/FA0 from data)', ls='--')
    plt.show()
    plt.tight_layout()
