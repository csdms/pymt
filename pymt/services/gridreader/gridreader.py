#! /bin/env python
import warnings

import yaml

from ...printers.nc.read import field_fromfile
from .interpolate import create_interpolators
from .time_series_names import get_time_series_names


class TimeInterpolator:
    def __init__(self):
        self._shape = ()
        self._spacing = ()
        self._origin = ()
        self._input_exchange_items = set()
        self._output_exchange_items = set()
        self._start_time = 0.0
        self._end_time = 0.0
        self._time = 0.0
        self._interpolators = {}

    def initialize(self, source):
        config = read_configuration(source)

        (fields, times) = field_fromfile(config["input_file"], fmt="NETCDF4")

        self._shape = fields[0].get_shape()
        self._spacing = fields[0].get_spacing()
        self._origin = fields[0].get_origin()

        self._input_exchange_items = set()
        self._output_exchange_items = get_time_series_names(fields.keys())

        self._start_time = times[0]
        self._end_time = times[-1]
        self._time = times[0]

        self._interpolators = create_interpolators(
            times, fields, kind=config["interpolation"]
        )

    def update_until(self, time):
        if time < self._start_time or time > self._endtime:
            raise ValueError(
                "time is outside of start/end time ({0} not in [{1}, {2}])".format(
                    time, self._start_time, self._end_time
                )
            )

        self._time = time

    def finalize(self):
        pass

    def get_start_time(self):
        return self._start_time

    def get_end_time(self):
        return self._end_time

    def get_current_time(self):
        return self._time

    def get_input_var_names(self):
        return self._input_exchange_items

    def get_output_var_names(self):
        return self._output_exchange_items

    def get_grid_shape(self, grid_id):
        if grid_id in (None, ""):
            warnings.warn("grid identifier is ignored")
        return self._shape

    def get_grid_spacing(self, grid_id):
        if grid_id in (None, ""):
            warnings.warn("grid identifier is ignored")
        return self._spacing

    def get_grid_origin(self, grid_id):
        if grid_id in (None, ""):
            warnings.warn("grid identifier is ignored")
        return self._origin

    def get_value(self, name):
        return self._interpolators[name](self._time)
        # if name.endswith('_increment'):
        #    name = name[:- len('_increment')]
        #    return (self._interpolators[name](self._time) -
        #            self._interpolators[name](self._last_time))
        # else:
        #    return self._interpolators[name](self._time)


def get_abspath_or_url(filename, prefix=""):
    import os
    from urlparse import urlparse, urlunparse

    parts = urlparse(filename)
    if parts.scheme in ["file", ""]:
        return os.path.join(prefix, parts.path)
    else:
        return urlunparse(parts)


def read_configuration(source):
    config = yaml.safe_load(source)

    input_file = config.get("input_file")
    input_dir = config.get("input_dir", "")
    kind = config.get("interpolation", "linear")

    return {
        "input_file": get_abspath_or_url(input_file, prefix=input_dir),
        "interpolation": kind,
    }


if __name__ == "__main__":
    import doctest

    doctest.testmod()
