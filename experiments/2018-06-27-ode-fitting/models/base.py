import copy
import weakref
import numpy
import scipy.stats
import scipy.integrate

from utils import stderr

__all__ = ['Variable', 'ODEModel']


class Variable(object):
    """
    Descriptor for numerical variables with optional bounds. Subclasses of
    `ODEModel` can define instances of this class as class attributes to create
    "variables" (such as parameters or initial conditions) whose value is
    bounded within an interval. In the following, we refer to such a subclass
    as the "owner" class. (This follows the terminology for descriptor classes
    in the Python documentation.)
    """

    def __init__(self, lower=None, upper=None):
        """
        The lower and upper bounds are optional. If passed, they will be
        checked whenever this attribute is set to a value, for example, the
        following code:

            >>> class Test:
                x = Variable(lower=1)

            >>> t = Test()
            >>> t.x = -1

        Will raise ValueError.

        If a bound is not passed, it is the same has having passed +infinity
        (for the upper bound) or -infinity (for the lower bound).
        """
        if lower is not None and upper is not None:
            assert lower <= upper, "Illegal bounds: lower > upper"
        self.lower = lower
        self.upper = upper
        # This dictionary holds the values of all the attributes managed by any
        # given instance of the descriptor. Since instances of this descriptor
        # are actually class variables in the owner class (typically a subclass
        # of `ODEModel`), the dictionary maps an owner class instance to its
        # attribute value. Because this introduces an extra reference to the
        # owner class instance, the mapping uses a "weak" key so that when no
        # other reference to the instance is available, the whole entry can be
        # automatically discarded. This is to avoid holding up memory for
        # objects of the the owner class that are no longer in use.
        self.values = weakref.WeakKeyDictionary()

    def __get__(self, instance, owner=None):
        if instance is None:
            # We do not allow this attribute to be accessed as a class
            # attribute.
            raise AttributeError("Not a class attribute")
        try:
            return self.values[instance]
        except KeyError:
            # To signal the value has not been set yet.
            raise AttributeError("Value not set: {}".format(instance))

    def __set__(self, instance, value):
        # Make sure the value is within bounds before updating it.
        if self.lower is not None:
            if value < self.lower:
                raise ValueError("Illegal value < lower: {}".format(value))
        if self.upper is not None:
            if value > self.upper:
                raise ValueError("Illegal value > upper: {}".format(value))
        self.values[instance] = value

    def __delete__(self, instance):
        del self.values[instance]


class ODEModel(object):
    """
    Base class for all O.D.E. models.

    To write a subclass you will need to:
        1. Override the `dy(y, t)` method. This returns the vector of
           derivatives of the system of ODEs.

        2. Define a list of names of parameters (_theta). These are the
           parameters of the ODEs.

        3. Define a list of names of state variables (_y) of the ODEs.

        4. (Optional) Implement the `obs(y)` static method. This function
           returns the subset of "observable" variables. This is helpful when
           for example not all state variables can be compared to empirical
           data, or when multiple state variables need to be aggregated to
           provide the actual observables.
    """
    # list of attribute names in the vector of parameters
    _theta = []

    # list of attribute names in the vector of state variables
    _y = []

    def __init__(self, **kwargs):
        super(ODEModel, self).__init__()
        self._do_agg = hasattr(self, "obs")
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getstate__(self):
        # save separately the state of all attributes managed by Variable
        # instances
        state = self.__dict__.copy()
        theta_state = {}
        for name in self._theta:
            try:
                theta_state[name] = getattr(self, name)
            except AttributeError:
                pass
        y_state = {}
        for name in self._y:
            try:
                y_state[name] = getattr(self, name)
            except AttributeError:
                pass
        return (state, theta_state, y_state)

    def __setstate__(self, state):
        # recreate separately the state of all attributes managed by Variable
        # instances
        state, theta_state, y_state = state
        self.__dict__.update(state)
        for k, v in theta_state.items():
            setattr(self, k, v)
        for k, v in y_state.items():
            setattr(self, k, v)

    def gettheta(self):
        """ Get the vector of parameters """
        x = [getattr(self, name, numpy.nan) for name in self._theta]
        return numpy.asfarray(x)

    def settheta(self, theta):
        """ Set the vector of parameters """
        for name, value in zip(self._theta, theta):
            setattr(self, name, value)

    theta = property(gettheta, settheta, None, "Vector of parameters")

    def gety(self):
        """ Get the vector of state variables """
        x = [getattr(self, name, numpy.nan) for name in self._y]
        return numpy.asfarray(x)

    def sety(self, y):
        """ Set the vector of parameters """
        for name, value in zip(self._y, y):
            setattr(self, name, value)

    y = property(gety, sety, None, "Vector of state variables")

    def dy(self, y, t, *args):
        """
        Subclassess need to instantiate this.
        """
        raise NotImplementedError()

    def __call__(self, y, t, *args, **kwargs):
        dy = self.dy(y, t)
        z = numpy.sum(dy)
        assert numpy.isclose(z, 0, atol=1e5), \
            "sum(dy) does not cancel out: {}".format(z)
        return dy

    def simulate(self, y=None, times=None, **kwargs):
        """
        Use numerical integration to simulate the model. For more information,
        `scipy.integrate.odeint`.

        Parameters
        ==========
        y : sequence
            Initial conditions (optional).

        times : times
            The system is evaluated at these times (optional).

        Notes
        =====
        If neither `y` nor `times` is passed, the method will use the values of
        the instance. If passed, the instance values take the passed values.

        Additional keyword arguments are passed to `scipy.integrate.odeint`.
        """
        if y is not None:
            self.y = y
        if times is not None:
            self.times = times
        y = scipy.integrate.odeint(self, self.y, self.times,
                                   args=tuple(self.theta), **kwargs)
        if self._do_agg:
            return self.obs(y)
        else:
            return y

    def getbounds(self):
        C = self.__class__
        var_names = self._theta + self._y
        tmp = []
        for name in var_names:
            try:
                getattr(self, name)
            except AttributeError:
                v = C.__dict__[name]
                lower = v.lower if v.lower is not None else -numpy.inf
                upper = v.upper if v.upper is not None else +numpy.inf
                tmp.append((lower, upper))
        return tmp

    def residuals(self, x):
        """
        x is a vector of values for unknown variables of the model. It may
        include model parameters (theta) and initial conditions (y).

        For this function to work the model must have a the following
        attributes set:
            * times
            * data
        """
        obj = copy.copy(self)
        x = list(x)
        var_names = obj._theta + obj._y
        for name in var_names:
            try:
                getattr(obj, name)
            except AttributeError:
                # This variable is an unknown
                value = x.pop()
                setattr(obj, name, value)
        # Make sure all unknowns have been assigned.
        if len(x) > 0:
            raise ValueError("Some unknowns not assigned: {}".format(x))
        yarr = obj.simulate()
        return (yarr - self.data).ravel()

    def fit(self, data, times=None, x0=None, nrep=10, **kwargs):
        """
        Fit this model to empirical data with least squares.

        Parameters
        ==========

        data : ndarray
            The empirical data to fit. This is an (M, N) array where M is the
            number of time steps and N the number of "observable" variables.

        times : ndarray
            An optional (M,) array of time points. Will be used for
            integration of the model. If not passed, it is equal to [0, ...,
            M-1].

        x0 : ndarray
            An optional (N, 1) array of initial guesses for unknowns of the
            fit. If not passed, this is drawn uniformly at random.

        nrep : int
            Repeat the fitting multiple times and return the solution with
            minimum cost.

        Returns
        =======
        xopt : ndarray
            An (M,) ndarray of fit estimates.

        xerr : ndarray
            An (M,) ndarray of standard errors of the fit.

        Notes
        =====
        Additional keyword arguments are passed to the least squares routine.
        By default, the trf method is used, with bounds and x_scale
        automatically inferred from the model variables. See
        `scipy.optimize.least_squares` for more information.
        """
        bounds = self.getbounds()
        lower_bounds, upper_bounds = zip(*bounds)
        self.data = data
        # default times
        if times is None:
            times = numpy.arange(len(data))
        self.times = times
        # draw x0 at random from bounds.
        if x0 is None:
            size = (nrep, len(bounds))
            x0seq = scipy.stats.uniform.rvs(lower_bounds, upper_bounds, size)
        else:
            x0seq = (x0 for i in range(nrep))
        x_scale = numpy.diff(bounds, axis=1).ravel()
        tmp = []
        for _x0 in x0seq:
            res = scipy.optimize.least_squares(self.residuals, _x0,
                                               x_scale=x_scale,
                                               bounds=(lower_bounds,
                                                       upper_bounds),
                                               **kwargs)
            tmp.append(res)
        best_res = min(tmp, key=lambda k: k.cost)
        return best_res.x, stderr(best_res)
