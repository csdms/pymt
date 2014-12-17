#! /bin/env python
import yaml

import numpy as np


class ConstantScalars(object):
    def initialize(self, filename):
        with open(filename, 'r') as opened:
            scalar_vars = yaml.load(opened.read())

        self._vars = {}
        for (name, value) in scalar_vars.items():
            self._vars[name] = np.array(value, dtype=np.float)

        self._shape = (1, )
        self._spacing = (1., )
        self._origin = (0., )

        self._input_exchange_items = set()
        self._output_exchange_items = self._vars.keys()

        self._start_time = 0.
        self._end_time = np.inf
        self._time = 0.

    def update(self, time):
        self._time = time

    def update_until(self, time):
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
        if var in self._vars:
            return self._shape
        else:
            raise KeyError(var)

    def get_grid_spacing(self, var):
        if var in self._vars:
            return self._spacing
        else:
            raise KeyError(var)

    def get_grid_origin(self, var):
        if var in self._vars:
            return self._origin
        else:
            raise KeyError(var)

    def get_grid_values(self, name):
        return self._vars[name]

    def get_double(self, name):
        return self._vars[name]


class River(ConstantScalars):
    pass

