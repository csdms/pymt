#! /usr/bin/env python

from scipy.interpolate import interp1d


class TimeInterpolator(object):
    def __init__(self, method="linear"):
        self._method = method or "linear"
        self._data = []
        self._time = []
        self._ti = None

    def add_data(self, data, time):
        self._data.append(data)
        self._time.append(time)

        self._func = None

    def interpolate(self, time):
        if self._func is None:
            self._func = interp1d(
                self._time,
                self._data,
                axis=0,
                kind=self._method,
                fill_value="extrapolate",
            )

        return self._func(time)
