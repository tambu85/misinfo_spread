import copy
import weakref
import logging
import numpy
import scipy.stats
import scipy.integrate

from utils import pstderr, mape, smape, logaccratio

__all__ = ['Variable', 'ODEModel']

logger = logging.getLogger()

_least_squares = scipy.optimize.least_squares


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
            # Return the descriptor instance if accessed as a class attribute.
            return self
        try:
            # Return the value managed by this descriptor instance if accessed
            # as an instance attribute.
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

        5. (Optional) Implement the `inity0(self, **kwargs)` method to
           initialize the initial conditions to the data.
    """
    # list of attribute names in the vector of parameters
    _theta = []

    # list of attribute names in the vector of state variables
    _y0 = []

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
        for name in self._y0:
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

    def gety0(self):
        """ Get the vector of state variables """
        x = [getattr(self, name, numpy.nan) for name in self._y0]
        return numpy.asfarray(x)

    def sety0(self, y0):
        """ Set the vector of parameters """
        for name, value in zip(self._y0, y0):
            setattr(self, name, value)

    y0 = property(gety0, sety0, None, "Vector of state variables")

    def dy(self, y, t):
        """
        Subclassess *must* to implement this to provide the instantaneous
        derivative of the model for integration.
        """
        raise NotImplementedError()

    @staticmethod
    def obs(y):
        """
        Subclasses can implement this to compute observable variables when not
        all state variable have a corresponding datum.
        """
        raise NotImplementedError()

    def inity0(self, how, *args, **kwargs):
        """
        Set initial compartment values for fit.

        Parameters
        ==========
        how - one of 'all', 'none', non-obs'

        additional keyword arguments.

        Notes
        =====
        Subclasses should not override this method. Instead, they should
        implement the following two private methods:

            _inity0_none  -- set all compartments

            _inity0_nonobs -- set only "observable" compartments
        """
        if how == "all":
            # do nothing -- all y0 will be treated as fit unknowns.
            pass
        elif how == "none":
            # non-observables are set to zero, observables to the data
            self._inity0_none(*args, **kwargs)
        elif how == "non-obs":
            # the default: fit non-observables, set observables to the data
            self._inity0_nonobs(*args, **kwargs)
        else:
            raise ValueError("No such option: {}".format(how))

    def _inity0_none(self, **kwargs):
        """
        Subclasses can implement this to initialize (part of) the initial
        conditions using the data.

        Non-observables should be set to zero (except S), observables to the
        data.
        """
        raise NotImplementedError()

    def _inity0_nonobs(self, **kwargs):
        """
        Subclasses can implement this to initialize (part of) the initial
        conditions using the data.

        Non-observables should be all fit, observables should be set to the
        data.
        """
        raise NotImplementedError()

    def __call__(self, y, t):
        dy = self.dy(y, t)
        z = numpy.sum(dy)
        if not numpy.isclose(z, 0):
            import warnings
            warnings.warn("sum(dy) does not cancel out: {}".format(z))
        return dy

    def predict(self, times, full=False, **kwargs):
        """
        See simulate
        """
        return self.simulate(times, full=full, **kwargs)

    def simulate(self, times, full=False, **kwargs):
        """
        Use numerical integration to simulate the model. For more information,
        `scipy.integrate.odeint`.

        Parameters
        ==========
        times : times
            The system is evaluated at these times (optional).

        full : bool
            Return the full system, not just the observables variables.
            (optional.)

        Notes
        =====
        If neither `y0` nor `times` is passed, the method will use the values
        of the instance. If passed, the instance values take the passed values.

        Additional keyword arguments are passed to `scipy.integrate.odeint`.
        """
        y = scipy.integrate.odeint(self, self.y0, times, **kwargs)
        if full:
            return y
        elif self._do_agg:
            return self.obs(y)
        else:
            return y

    def _getbounds(self):
        C = self.__class__
        var_names = self._theta + self._y0
        tmp = []
        for name in var_names:
            try:
                getattr(self, name)
            except AttributeError:
                v = getattr(C, name)
                lower = v.lower if v.lower is not None else -numpy.inf
                upper = v.upper if v.upper is not None else +numpy.inf
                tmp.append((lower, upper))
        return tmp

    def _genparams(self, nrep):
        """
        Generate parameters at random.
        """
        bounds = self._getbounds()
        lower_bounds, upper_bounds = zip(*bounds)
        size = (nrep, len(bounds))
        loc = lower_bounds
        scale = numpy.asarray(upper_bounds) - numpy.asarray(lower_bounds)
        x0seq = scipy.stats.uniform.rvs(loc, scale, size)
        idx = numpy.isinf(x0seq)
        x0seq[idx] = numpy.broadcast_to(lower_bounds, x0seq.shape)[idx] + 1.0
        return x0seq

    def _assign(self, x, fitted=False):
        """
        Assign missing values to a model. If fitted is True, also set
        attribute with the same name and a trailing underscore, e.g.:

            alpha -> alpha_

        This follows the same convention of scikit-learn and means that the
        attribute has been estimated. (Default: fitted = False.)
        """
        x = list(x)
        var_names = self._theta + self._y0
        for name in var_names:
            try:
                getattr(self, name)
            except AttributeError:
                # This variable is an unknown
                value = x.pop(0)
                setattr(self, name, value)
                if fitted:
                    # estimated attribute
                    setattr(self, name + '_', value)
        # Make sure all unknowns have been assigned.
        if len(x) > 0:
            raise ValueError("Some unknowns not assigned: {}".format(x))

    def _residuals(self, x):
        """
        x is a vector of values for unknown variables of the model. It may
        include model parameters (theta) and initial conditions (y).

        For this function to work the model must have a the following
        attributes set:
            * times
            * data

        A new object is created to compute the residuals.
        """
        obj = copy.copy(self)
        obj._assign(x)
        yarr = obj.simulate(self.times)
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
        self : a fitted instance of ODEModel

        Notes
        =====
        Additional keyword arguments are passed to the least squares routine.
        By default, the trf method is used, with bounds and x_scale
        automatically inferred from the model variables. See
        `scipy.optimize.least_squares` for more information.
        """
        bounds = self._getbounds()
        lower_bounds, upper_bounds = zip(*bounds)
        self.data = data
        # default times
        if times is None:
            times = numpy.arange(len(data))
        self.times = times
        if x0 is None:
            # Draw x0 at random from bounds. If any unknown is unconstrained,
            # set the initial guess to lower + 1.0 (a safe value).
            x0seq = self._genparams(nrep)
        else:
            # Use provided x0 for all repetitions
            x0seq = (x0 for i in range(nrep))
        x_scale = numpy.diff(bounds, axis=1).ravel()
        # We cannot mix finite and infinite x_scale values, so if any unknown
        # is unconstrained, we let the routine estimate x_scale using the
        # Jacobian.
        if numpy.isinf(x_scale).any():
            x_scale = 'jac'
        tmp = []
        for _x0 in x0seq:
            try:
                res = _least_squares(self._residuals, _x0, x_scale=x_scale,
                                     bounds=(lower_bounds, upper_bounds),
                                     **kwargs)
                tmp.append(res)
            except Exception:
                logger.exception("Caught exception in fit. Traceback follows:")
        if tmp:
            best_res = min(tmp, key=lambda k: k.cost)
            self.err_ = pstderr(best_res)
            self._assign(best_res.x, fitted=True)
            self.cost_ = best_res.cost
        else:
            logger.error("All fits failed!")
        del self.data
        del self.times
        return self

    def summary(self, fmt='.2e'):
        """
        Prints to console a summary of all model variables and errors.

        Parameters
        ==========
        fmt - floating point number format
        """
        headers = {
            "name": "NAME",
            "value": "VALUE",
            "error": "ERR. (+/-)"
        }
        num_template = "{{:{0}}}".format(fmt)
        name_template = "{name:>{name_width}}"
        value_template = "{{value:> {{value_width}}{0}}}".format(fmt)
        error_template = "{{error:>{{error_width}}{0}}}{{ast}}".format(fmt)
        row_template = "{}  {}  {}".format(name_template, value_template,
                                           error_template)
        var_names = self._theta + self._y0
        i = 0
        records = []
        value_widths = []
        error_widths = []
        name_widths = list(map(len, var_names))
        name_widths.append(len(headers["name"]))
        for name in var_names:
            record = {}
            record["name"] = name
            if hasattr(self, name + '_'):
                # estimated variable
                record["value"] = getattr(self, name + '_')
                record["error"] = self.err_[i]
                i += 1
            else:
                try:
                    record["value"] = getattr(self, name)
                except AttributeError:
                    record["value"] = -1.0
                record["error"] = 0.0
            records.append(record)
            value_len = len(num_template.format(record["value"]))
            error_len = len(num_template.format(record["error"]))
            value_widths.append(value_len)
            error_widths.append(error_len)
        value_widths.append(len(headers["value"]))
        error_widths.append(len(headers["error"]))
        widths = {
            "name": max(name_widths) + 2,
            "value": max(value_widths) + 2,
            "error": max(error_widths) + 2
        }
        logger.info("{0}  {1}  {2}".format("=" * widths["name"],
                                           "=" * widths["value"],
                                           "=" * widths["error"]))
        logger.info("{0:^{3}}  {1:^{4}}  {2:^{5}}".format(headers["name"],
                                                          headers["value"],
                                                          headers["error"],
                                                          widths["name"],
                                                          widths["value"],
                                                          widths["error"]))
        logger.info("{0}  {1}  {2}".format("=" * widths["name"],
                                           "=" * widths["value"],
                                           "=" * widths["error"]))
        ast_flag = False
        one_flag = False
        for record in records:
            record["name_width"] = widths["name"]
            record["value_width"] = widths["value"]
            record["error_width"] = widths["error"]
            record["ast"] = ""
            if record["value"] == -1.0:
                one_flag = True
                record["ast"] = "^"
            elif record["error"] == 0.0:  # FIXME fit can yield error == 0.0
                record["ast"] = "*"
                ast_flag = True
            logger.info(row_template.format(**record))
        logger.info("{0}  {1}  {2}".format("=" * widths["name"],
                                           "=" * widths["value"],
                                           "=" * widths["error"]))
        if ast_flag:
            logger.info("* From data.")
        if one_flag:
            logger.info("^ Value = -1.0: variable not set.")
        if ast_flag or one_flag:
            logger.info("{0}  {1}  {2}".format("=" * widths["name"],
                                               "=" * widths["value"],
                                               "=" * widths["error"]))

    def error(self, data, times=None, metric='mape'):
        """
        Model prediction error.

        metric : str
            Error metric to use. It can be "mape", "smape", "logaccratio", and
            "rmse". Default: mape.
        """
        if times is None:
            times = numpy.arange(len(data))
        y = self.simulate(times)
        if metric == 'mape':
            return mape(y, data)
        elif metric == 'smape':
            return smape(y, data)
        elif metric == 'logaccratio':
            return logaccratio(y, data)
        elif metric == 'rmse':
            return numpy.sqrt(self.cost_) # should be rmse(y, data) (with rmse function, currently missing)
        else:
            raise ValueError("No such metric: {}".format(metric))
