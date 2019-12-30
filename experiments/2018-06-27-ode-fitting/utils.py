import numpy
import scipy.linalg
import warnings


def pstderr(res):
    """
    Compute standard error of the fitted parameters
    """
    # Code adapted from: scipy.optimize.curve_fit
    # Do Moore-Penrose inverse discarding zero singular values.
    _, s, VT = scipy.linalg.svd(res.jac, full_matrices=False)
    threshold = numpy.finfo(float).eps * max(res.jac.shape) * s[0]
    s = s[s > threshold]
    VT = VT[:s.size]
    pcov = numpy.dot(VT.T / s**2, VT)
    return 1.96 * numpy.sqrt(numpy.diag(pcov))


def mape(x, y, frac=False):
    r"""
    Returns Mean Absolute Percentage Error (MAPE) of x relative to y. This is
    defined as:

    MAPE = (100 / N) * \sum |x[i] - y[i]| / y[i]

    Parameters
    ==========
    x, y : ndarray

    frac : bool
        If True, return a fraction (i.e., do not multiply by 100 in the above
        formula). If False, return a percentage. (Default: False.)

    Notes
    =====
    Values of y that are equal or close to zero are not included, and the
    denominator will reflect the number of effective (i.e., nonzero) samples.
    """
    x = numpy.ravel(x)
    y = numpy.ravel(y)
    N = len(y)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        err = numpy.abs((x - y) / y)
    idx = numpy.isclose(y, 0)
    err[idx] = 0.0
    N_nnz = float(N - idx.sum())
    err = err.sum() / N_nnz
    if frac:
        return err
    else:
        return 100 * err


def smape(x, y, frac=False):
    r"""
    Returns Symmetric Mean Absolute Percentage Error (MAPE) of x relative to y.
    This is defined as:

    SMAPE = (100 / N) * \sum |x[i] - y[i]| / (|x[i]| + |y[i]|)

    Parameters
    ==========
    x, y : ndarray

    frac : bool
        If True, return a fraction (i.e., do not multiply by 100 in the above
        formula). If False, return a percentage. (Default: False.)
    """
    x = numpy.ravel(x)
    y = numpy.ravel(y)
    N = len(y)
    num = numpy.abs(x - y)
    den = numpy.abs(x) + numpy.abs(y)
    N_nnz = N - (den == 0).sum()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        err = numpy.nansum(num / den) / float(N_nnz)
    if frac:
        return err
    else:
        return 100 * err


def logaccratio(x, y, frac=False):
    r"""
    Returns Log Accuracy Ratio of x relative to y. This is defined as:

    (100 / N) * \sum log(x[i] / y[i])

    Parameters
    ==========
    x, y : ndarray

    frac : bool
        If True, return a fraction (i.e., do not multiply by 100 in the above
        formula). If False, return a percentage. (Default: False.)
    """
    x = numpy.ravel(x)
    y = numpy.ravel(y)
    x_idx = (x == 0)
    y_idx = (y == 0)
    idx = x_idx | y_idx
    N_nnz = len(y) - idx.sum()
    err = numpy.log(x[~idx] / y[~idx]).sum() / float(N_nnz)
    if frac:
        return err
    else:
        return 100 * err
