#! /bin/env python
import numpy as np
import yaml


class ConstantScalars:
    """Service component that returns scalars."""

    def initialize(self, filename):
        """Initialize the component from a file.

        Parameters
        ----------
        filename : str
            Name of initialization file.
        """
        with open(filename, "r") as opened:
            scalar_vars = yaml.safe_load(opened.read())

        self._vars = {}
        for (name, value) in scalar_vars.items():
            self._vars[name] = np.array(value, dtype=np.float)

        self._shape = (1,)
        self._spacing = (1.0,)
        self._origin = (0.0,)

        self._input_exchange_items = []
        self._output_exchange_items = list(self._vars.keys())

        self._start_time = 0.0
        self._end_time = np.inf
        self._time = 0.0

    def update(self, time):
        """Update one time step."""
        self._time = time

    def update_until(self, time):
        """Update until a time."""
        self._time = time

    def finalize(self):
        """Clean up."""
        pass

    def get_start_time(self):
        """Component start time."""
        return self._start_time

    def get_end_time(self):
        """Component stop time."""
        return self._end_time

    def get_current_time(self):
        """Component current time."""
        return self._time

    def get_input_var_names(self):
        """Input variable names."""
        return self._input_exchange_items

    def get_output_var_names(self):
        """Output variable names."""
        return self._output_exchange_items

    def get_var_grid(self, var):
        """Grid identifier for a variable.

        Parameters
        ----------
        var : str
            Name of grid variable.

        Returns
        -------
        int
            Grid identifier.
        """
        if var in self._vars:
            return 0
        else:
            raise KeyError(var)

    def get_grid_shape(self, grid_id):
        """Shape of grid.

        Parameters
        ----------
        grid_id : int
            Grid identifier.

        Returns
        -------
        shape : tuple
            Shape of the grid.
        """
        if grid_id == 0:
            return self._shape
        else:
            raise KeyError(0)

    def get_grid_spacing(self, grid_id):
        """Spacing of grid.

        Parameters
        ----------
        grid_id : int
            Grid identifier.

        Returns
        -------
        spacing : tuple
            Spacing of nodes in each dimension.
        """
        if grid_id == 0:
            return self._spacing
        else:
            raise KeyError(0)

    def get_grid_origin(self, grid_id):
        """Origin of grid.

        Parameters
        ----------
        grid_id : int
            Grid identifier.

        Returns
        -------
        origin : tuple
            Origin of nodes in each dimension.
        """
        if grid_id == 0:
            return self._origin
        else:
            raise KeyError(0)

    def get_value(self, name):
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


class River(ConstantScalars):
    pass
