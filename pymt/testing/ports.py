import numpy as np


class UniformRectilinearGridPort(object):
    def __init__(self):
        self._shape = (4, 5)
        self._spacing = (1.0, 2.0)
        self._origin = (0.0, 1.0)
        self._values = {
            "landscape_surface__elevation": np.ones(self._shape),
            "sea_surface__temperature": np.zeros(self._shape),
            "sea_floor_surface_sediment__mean_of_grain_size": np.zeros(self._shape),
            "air__density": np.zeros(self._shape),
            "glacier_top_surface__slope": np.zeros(self._shape),
        }

    def get_var_grid(self, var_name):
        if var_name in self._values:
            return 0
        else:
            raise KeyError(var_name)

    def get_grid_shape(self, grid_id):
        if grid_id == 0:
            return self._shape
        else:
            raise KeyError(grid_id)

    def get_grid_spacing(self, grid_id):
        if grid_id == 0:
            return self._spacing
        else:
            raise KeyError(grid_id)

    def get_grid_origin(self, grid_id):
        if grid_id == 0:
            return self._origin
        else:
            raise KeyError(grid_id)

    def get_value(self, var_name):
        return self._values[var_name]
