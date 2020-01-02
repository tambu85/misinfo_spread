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
    num = x - y
    den = (x + y) / 2.0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        err = numpy.abs(num / den)
    err = numpy.nanmean(err)
    if frac:
        return err
    else:
        return 100 * err


def logaccratio(x, y, frac=False):
    r"""
    Returns Log Accuracy Ratio of x relative to y. Based on Morley et al. [1],
    this is defined as:

    100 * exp[ median( ln(x / y) ) - 1 ]

    Where ln is the natural log. This is a symmetric measure that can be
    interpreted as a percentage error.

    Parameters
    ==========
    x, y : ndarray

    frac : bool
        If True, return a fraction (i.e., do not multiply by 100 in the above
        formula). If False, return a percentage. (Default: False.)

    References
    ==========
    [1] Morley et al., 2017. Measures of Model Performance Based On the Log
    Accuracy Ratio. Space Weather 16(1), pp. 69--88. DOI: 10.1002/2017SW001669

    Note
    ====
    An error will be thrown if the ratio x / y is negative.
    """
    x = numpy.ravel(x)
    y = numpy.ravel(y)
    idx = x > y
    _x = numpy.where(idx, x, y)
    _y = numpy.where(idx, y, x)
    idx = numpy.isclose(_y, 0)
    _x = _x[~idx]
    _y = _y[~idx]
    q = _x / _y
    assert (q >= 0).all(), "Invalid negative ratio"
    q = numpy.abs(numpy.log(q))
    med = numpy.nanmedian(q)
    err = numpy.exp(med) - 1
    if frac:
        return err
    else:
        return 100 * err
