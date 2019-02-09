#! /usr/bin/env python
import bisect

from scipy.interpolate import interp1d

_MINIMUM_SIZE_FOR_METHOD = {
    "linear": 2,
    "nearest": 2,
    "zero": 2,
    "slinear": 2,
    "quadratic": 3,
    "cubic": 4,
    "previous": 2,
    "next": 2,
}


class TimeInterpolator(object):

    METHODS = (
        "linear",
        "nearest",
        "zero",
        "slinear",
        "quadratic",
        "cubic",
        "previous",
        "next",
    )

    def __init__(
        self, data=(), method="linear", fill_value="extrapolate", maxsize=None
    ):
        """Interpolate data based on an evolving time series of data values.

        Parameters
        ---------
        data : iterable of (*time*, *data*), optional
            The data to use for the interpolation as an iterable of (*time*, *data*).
            *data* can either be scalars or numpy arrays.
        method : str, optional
            The interpolation method to use.
        fill_value : str or float, optional
            The value to use if trying to interpolate values that are outside the
            stored times. The default is to extrapolate to the given time.
        maxsize : int, optional
            The maximum size of the buffer that holds the interpolation times. When
            the buffer reaches this size, the oldest times will be popped off a the
            stack.
        """
        self._data = []
        self._time = []
        self._func = None
        self._method = None
        self._fill_value = None
        self._maxsize = None

        self.method = method
        self.fill_value = fill_value
        self.maxsize = maxsize

        self.add_data(data)

    @property
    def method(self):
        """The method used for interpolating time."""
        return self._method

    @method.setter
    def method(self, val):
        if val not in TimeInterpolator.METHODS:
            raise ValueError("method not understood")
        self._method = val

    @property
    def fill_value(self):
        """Value to use when interpolating values outside of the data."""
        return self._fill_value

    @fill_value.setter
    def fill_value(self, val):
        if val != "extrapolate" and not isinstance(val, float):
            raise ValueError(
                "fill_value not understood, must be either float or 'extrapolate'"
            )
        self._fill_value = val

    @property
    def maxsize(self):
        """The maximum number of times to be stored."""
        return self._maxsize

    @maxsize.setter
    def maxsize(self, val):
        if val is not None and val <= _MINIMUM_SIZE_FOR_METHOD[self.method]:
            raise ValueError("maxsize too small for method ({0})".format(self.method))
        self._maxsize = val
        self._trim_data_to_maxsize()

    def add_data(self, time_and_data):
        """Add new data points to the interpolator.

        Parameters
        ----------
        time : float or iterable of float
            Time values
        data : float or iterable
            Data values to interpolate.
        """
        if isinstance(time_and_data, float):
            time_and_data = tuple(time_and_data)

        for t, d in time_and_data:
            self._insert_data(t, d)
        self._trim_data_to_maxsize()

    def _trim_data_to_maxsize(self):
        """Drop stored data to maxsize."""
        if self.maxsize is not None:
            while len(self._time) > self.maxsize:
                self._time.pop(0)
                self._data.pop(0)

    def _insert_data(self, time, data):
        """Insert data so that it is stored sorted by time."""
        ind = bisect.bisect_right(self._time, time)
        self._time.insert(ind, time)
        self._data.insert(ind, data)

        self._func = None

    def interpolate(self, time):
        """Interpolate the data at a given time."""
        if self._func is None:
            self._func = interp1d(
                self._time,
                self._data,
                axis=0,
                kind=self._method,
                fill_value=self._fill_value,
                copy=False,
                assume_sorted=True,
                bounds_error=False,
            )

        return self._func(time)

    def __call__(self, time):
        """Interpolate the data at a given time."""
        return self.interpolate(time)
