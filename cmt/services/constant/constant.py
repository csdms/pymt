#! /bin/env python
import yaml

import numpy as np


class ConstantScalars(object):
    """Service component that returns scalars.
    """
    def initialize(self, filename):
        """Initialize the component from a file.

        Parameters
        ----------
        filename : str
            Name of initialization file.
        """
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
        """Update one time step.
        """
        self._time = time

    def update_until(self, time):
        """Update until a time.
        """
        self._time = time

    def finalize(self):
        """Clean up.
        """
        pass

    def get_start_time(self):
        """Component start time.
        """
        return self._start_time

    def get_end_time(self):
        """Component stop time.
        """
        return self._end_time

    def get_current_time(self):
        """Component current time.
        """
        return self._time

    def get_input_var_names(self):
        """Input variable names.
        """
        return self._input_exchange_items

    def get_output_var_names(self):
        """Output variable names.
        """
        return self._output_exchange_items

    def get_grid_shape(self, var):
        """Shape of a variable grid.

        Parameters
        ----------
        var : str
            Name of grid variable.

        Returns
        -------
        shape : tuple
            Shape of the grid.
        """
        if var in self._vars:
            return self._shape
        else:
            raise KeyError(var)

    def get_grid_spacing(self, var):
        """Spacing of a variable grid.

        Parameters
        ----------
        var : str
            Name of grid variable.

        Returns
        -------
        spacing : tuple
            Spacing of nodes in each dimension.
        """
        if var in self._vars:
            return self._spacing
        else:
            raise KeyError(var)

    def get_grid_origin(self, var):
        """Origin of a variable grid.

        Parameters
        ----------
        var : str
            Name of grid variable.

        Returns
        -------
        origin : tuple
            Origin of nodes in each dimension.
        """
        if var in self._vars:
            return self._origin
        else:
            raise KeyError(var)

    def get_grid_values(self, name):
        """Values on nodes of a grid.

        Parameters
        ----------
        var : str
            Name of grid variable.

        Returns
        -------
        values : ndarray
            Values of the nodes of a grid.
        """
        return self._vars[name]

    def get_double(self, name):
        return self._vars[name]


class River(ConstantScalars):
    pass
