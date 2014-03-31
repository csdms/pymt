import numpy as np


def get_port(name):
    return _SERVICES[name]


def get_port_names():
    return _SERVICES.keys()


class EmptyPort(object):
    def __init__(self):
        self._shape = (4, 5)
        self._spacing = (1., 2.)
        self._origin = (0., 1.)
        self._values = {}

    def initialize(self):
        for array in self._values.values():
            array.fill(0.)

    def run(self, time):
        for array in self._values.values():
            array.fill(time)

    def finalize(self):
        for array in self._values.values():
            array.fill(0.)

    def get_grid_shape(self, var_name):
        return self._shape

    def get_grid_spacing(self, var_name):
        return self._spacing

    def get_grid_origin(self, var_name):
        return self._origin

    def get_grid_values(self, var_name):
        return self._values[var_name]


class UniformRectilinearGridPort(EmptyPort):
    def __init__(self):
        EmptyPort.__init__(self)
        self._values = {
            'landscape_surface__elevation': np.empty(self._shape),
            'sea_surface__temperature': np.empty(self._shape),
            'sea_floor_surface_sediment__mean_of_grain_size':
                np.empty(self._shape),
            'air__density': np.empty(self._shape),
            'glacier_top_surface__slope': np.empty(self._shape),
        }


class WaterPort(EmptyPort):
    def __init__(self):
        EmptyPort.__init__(self)
        self._values = {
            'ocean_surface__temperature': np.empty(self._shape),
            'ocean_surface__density': np.empty(self._shape),
        }


class AirPort(EmptyPort):
    def __init__(self):
        EmptyPort.__init__(self)
        self._values = {
            'air__temperature': np.empty(self._shape),
            'air__density': np.empty(self._shape),
        }


class EarthPort(EmptyPort):
    def __init__(self):
        EmptyPort.__init__(self)
        self._values = {
            'earth_surface__temperature': np.empty(self._shape),
            'earth_surface__density': np.empty(self._shape),
        }


_SERVICES = {
    'test_port_0': UniformRectilinearGridPort(),
    'air_port': AirPort(),
    'water_port': WaterPort(),
    'earth_port': EarthPort(),
}
