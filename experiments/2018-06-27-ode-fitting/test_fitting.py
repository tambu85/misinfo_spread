""" Fit synthetic data """

import os
import sys
import logging
import configparser
import numpy
import scipy
# import matplotlib
import matplotlib.pyplot as plt

import models

# replace printing with logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
logging.captureWarnings(True)
logger = logging.getLogger(__name__)
print = logger.info

# Find out terminal size
py_vers = sys.version_info
if py_vers.major >= 3 and py_vers.minor >= 3:
    import shutil
    # on Python 3.3+ use os.get_terminal_size
    TERM_COLS = shutil.get_terminal_size().columns
elif os.name is "posix":
    # if that's not available ...
    # ... on Linux/Unix use stty to get terminal size
    import subprocess
    result = subprocess.getoutput("stty size")
    _, TERM_COLS = map(int, result.split())
else:
    # ... on Windows assume default of 80 columns
    TERM_COLS = 80

TERM_COLS -= 25  # length of timestamp

# Used by cmd line parser
AVAIL_MODELS = [v.__name__ for v in models.__dict__.values()
                if isinstance(v, type) and issubclass(v, models.ODEModel)]
# The base class -- cannot be chosen
AVAIL_MODELS.remove('ODEModel')


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


def gentheta(model, nrep):
    return model._genparams(nrep)[:, :len(model._theta)]


def gendata(model, tmax=168, sigma=50, p_outliers=0.1, outlier_mult=10):
    # Vector of integration time steps
    t = numpy.arange(tmax)

    # Generate data by simulating the ODE and applying Gaussian noise with
    # given sigma.
    y = model.simulate(t)
    yerr = scipy.stats.norm.rvs(scale=sigma, size=y.shape)

    # Add a fraction of outliers to simulate noisy tweet counts.
    n_outliers = int(len(t) * p_outliers)
    idx = numpy.random.choice(len(t), n_outliers, replace=False)
    yerr[idx] *= outlier_mult

    # Add noise to simulated data. Finally, clip negative values to zero, to
    # simulate count data.
    data = y + yerr
    data = data.clip(min=0)
    return t, data


def main(config_path, modelcls='HoaxModel', seed=None):
    # For reproducibility. Change seed to get different random numbers.
    numpy.random.seed(seed)
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(config_path)

    M = getattr(models, modelcls)

    # Model parameters
    m = M()
    m.y0 = numpy.zeros(len(m.y0))

    # Read parameters from config file
    conf_section = parser[modelcls]
    for k in conf_section.keys():
        val = conf_section.getfloat(k)
        setattr(m, k, val)

    # The true parameter values
    m.summary()

    # generate synthentic data with noise + outliers
    t, data = gendata(m)

    # Scenario 1) All: Fit unknowns = model parameter (theta) + initial
    # conditions (y0). All fits are best of three (3) attempts.
    # Scenario 2) Non-Obs: Like 1), but only BI0/FI0/S0 are unknown initial
    # conditions. BA0/FA0 are known and they are equal to the first observation
    # of the data.
    # Scenario 3) None: BI0/FI0/S0 = 0; BA0/FA0 = first observation of the
    # data.
    hows = ["all", "non-obs", "none"]
    _models = [m]
    for i, how in enumerate(hows):
        print("=" * TERM_COLS)
        print("{}) Fitting: {}".format(i + 1, how))
        _m = M()
        _m.fit(data, nrep=3)
        _m.inity0(how, data[0, 0], data[0, 1])
        _m.summary()
        _models.append(_m)

    # Plot true model, data, and fitted models.
    fig, axs = plt.subplots(1, 2)
    plot(fig, m, t, data, label='True', ls='-', lw=2)
    linestyles = ["--", "-.", ":"]
    for i, how in enumerate(hows):
        _m = _models[i + 1]
        label = "Fit #{} {}".format(i + 1, how)
        ls = linestyles[i]
        plot(fig, _m, t, label=label, ls=ls)

    plt.show()
    plt.tight_layout()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config_path', help='path to config file',
                        metavar='path')
    parser.add_argument('-m', '--model', default='HoaxModel',
                        help='Model to choose [default: %(default)s]',
                        choices=AVAIL_MODELS, dest='modelcls')
    parser.add_argument('-S', '--seed', type=int, help='PRNG seed')
    args = parser.parse_args()
    main(**vars(args))
