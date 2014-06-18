#! /bin/env python
import warnings

import yaml

from ...printers.nc.read import field_fromfile
from .time_series_names import get_time_series_names
from .interpolate import create_interpolators


class TimeInterpolator(object):
    def __init__(self):
        self._shape = ()
        self._spacing = ()
        self._origin = ()
        self._input_exchange_items = set()
        self._output_exchange_items = set()
        self._start_time = 0.
        self._end_time = 0.
        self._time = 0.
        self._interpolators = {}

    def initialize(self, source):
        config = read_configuration(source)

        (fields, times) = field_fromfile(config['input_file'], format='NETCDF4')

        self._shape = fields[0].get_shape()
        self._spacing = fields[0].get_spacing()
        self._origin = fields[0].get_origin()

        self._input_exchange_items = set()
        self._output_exchange_items = get_time_series_names(fields.keys())

        self._start_time = times[0]
        self._end_time = times[-1]
        self._time = times[0]

        self._interpolators = create_interpolators(
            times, fields, kind=config['interpolation'])

    def update_until(self, time):
        assert(time >= self._start_time)
        assert(time <= self._end_time)

        #self._last_time = self._time
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

    def get_grid_shape(self, var):
        if var in (None, ''):
            warnings.warn('var name is ignored')
        return self._shape

    def get_grid_spacing(self, var):
        if var in (None, ''):
            warnings.warn('var name is ignored')
        return self._spacing

    def get_grid_origin(self, var):
        if var in (None, ''):
            warnings.warn('var name is ignored')
        return self._origin

    def get_double(self, name):
        return self._interpolators[name](self._time)
        #if name.endswith('_increment'):
        #    name = name[:- len('_increment')]
        #    return (self._interpolators[name](self._time) -
        #            self._interpolators[name](self._last_time))
        #else:
        #    return self._interpolators[name](self._time)


def get_abspath_or_url(filename, prefix=''):
    import os
    from urlparse import urlparse, urlunparse

    parts = urlparse(filename)
    if parts.scheme in ['file', '']:
        return os.path.join(prefix, parts.path)
    else:
        return urlunparse(parts)


def read_configuration(source):
    config = yaml.load(source)

    input_file = config.get('input_file')
    input_dir = config.get('input_dir', '')
    kind = config.get('interpolation', 'linear')

    return {
        'input_file': get_abspath_or_url(input_file, prefix=input_dir),
        'interpolation': kind,
    }


if __name__ == "__main__":
    import doctest
    doctest.testmod()
