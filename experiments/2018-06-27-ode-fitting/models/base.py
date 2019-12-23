import weakref
import numpy
import scipy.integrate

__all__ = ['Variable', 'BaseModel']

class Variable(object):
    """ Descriptor for numerical variables with optional bounds. """

    # This dictionary stores actual values of the attributes. This is a
    # dictionary of dictionaries: it maps python objects to dictionaries. If an
    # object has an attribute that uses this descriptor, then a dictionary will
    # be created and associated to the object itself. This second dictionary
    # maps all Variable instances used by that object to their actual value.
    # This is needed because an object could have multiple attributes that use
    # this descriptor. The top-level dictionary uses weak key refrences, so
    # that when the object itself is no longer alive, the whole entry can be
    # discarded.
    values_dict = weakref.WeakKeyDictionary()

    def __init__(self, lower=None, upper=None):
        if lower is not None and upper is not None:
            assert lower <= upper, "Illegal bounds: lower > upper"
        self.lower = lower
        self.upper = upper

    def __get__(self, instance, owner=None):
        """ The value of this variable. """
        return self.values_dict[instance][self]

    def __set__(self, instance, value):
        self._checkvalue(value)
        try:
            self.values_dict[instance][self] = value
        except KeyError:
            self.values_dict[instance] = {}
            self.values_dict[instance][self] = value

    def __delete__(self, instance):
        d = self.values_dict[instance]
        del d[self]

    def _checkvalue(self, value):
        if self.lower is not None:
            if value < self.lower:
                raise ValueError("Illegal value < lower: {}".format(value))
        if self.upper is not None:
            if value > self.upper:
                raise ValueError("Illegal value > upper: {}".format(value))


class BaseModel(object):
    """
    Base class for all models.

    To write a subclass you will need to:
        1. Override the `dy(y, t)` method. This returns the vector of
           derivatives.

        2. Define a list of names of parameters (_theta)

        3. Define a list of names of state varialbes (_y)

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

    def __init__(self):
        super(BaseModel, self).__init__()
        self._do_agg = hasattr(self, "obs")

    def gettheta(self):
        """ Get the vector of parameters """
        return numpy.asfarray([getattr(self, name) for name in self._theta])

    def settheta(self, theta):
        """ Set the vector of parameters """
        for name, value in zip(self._theta, theta):
            setattr(self, name, value)

    theta = property(gettheta, settheta, None, "Vector of parameters")

    def gety(self):
        """ Get the vector of state variables """
        return numpy.asfarray([getattr(self, name) for name in self._y])

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
        assert numpy.isclose(numpy.sum(dy), 0), "sum(dy) does not cancel out"
        return dy

    def simulate(self, y=None, times=None, **kwargs):
        if y is not None:
            self.y
        if times is not None:
            self.times = times
        theta = tuple(self.theta)
        y = scipy.integrate.odeint(self, self.y, self.times, args=theta,
                                   **kwargs)
        if self._do_agg:
            return self.obs(y)
        else:
            return y

    def residuals(self, x):
        y, theta = self._split(x)
        self.y = y
        self.theta = theta
        yarr = self.simulate(self.y, self.times)
        return (yarr - self.data).ravel()
