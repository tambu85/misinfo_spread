import numpy
import scipy.linalg


def stderr(res):
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
