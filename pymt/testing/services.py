import numpy as np
from pymt.grids import UniformRectilinearPoints


def get_instance(name):
    return _INSTANCES[name]


def instantiate(cls, name):
    if name in _INSTANCES:
        raise ValueError(name)
    else:
        _INSTANCES[name] = get_class(cls)()


def get_class(name):
    return _CLASSES[name]


def get_class_names():
    return _CLASSES.keys()


#class EmptyPort(object):
class EmptyPort(UniformRectilinearPoints):
    _name = None

    def __init__(self):
        UniformRectilinearPoints.__init__(self, (4, 5), (1., 2.), (0., 1.))
        #self._shape = (4, 5)
        #self._spacing = (1., 2.)
        #self._origin = (0., 1.)
        self._values = {}
        self._time = self.start_time

    def get_component_name(self):
        return self._name

    def initialize(self):
        for array in self._values.values():
            array.fill(0.)

    def run(self, time):
        self._time = time
        for array in self._values.values():
            array.fill(self.current_time)

    def finalize(self):
        for array in self._values.values():
            array.fill(0.)

    def get_var_grid(self, var_name):
        if var_name in self._values:
            return 0
        else:
            raise KeyError(var_name)

    def get_grid_shape(self, grid_id):
        if grid_id == 0:
            return self.get_shape()
        else:
            raise KeyError(grid_id)

    def get_grid_spacing(self, grid_id):
        if grid_id == 0:
            return self.get_spacing()
        else:
            raise KeyError(grid_id)

    def get_grid_origin(self, grid_id):
        if grid_id == 0:
            return self.get_origin()
        else:
            raise KeyError(grid_id)

    def get_value(self, var_name):
        try:
            return self._values[var_name]
        except KeyError:
            print self._values.keys()
            raise

    def set_value(self, var_name, values):
        try:
            self._values[var_name].flat = values.flat
        except KeyError:
            print self._values.keys()
            raise

    @property
    def start_time(self):
        return 0.

    @property
    def current_time(self):
        return self._time

    @property
    def end_time(self):
        return 100.

    @property
    def time_step(self):
        return 1.


class WaterPort(EmptyPort):
    _name = 'water_port'
    def __init__(self):
        EmptyPort.__init__(self)
        self._values = {
            'ocean_surface__temperature': np.empty(self._shape),
            'ocean_surface__density': np.empty(self._shape),
        }


class AirPort(EmptyPort):
    _name = 'air_port'
    def __init__(self):
        EmptyPort.__init__(self)
        self._values = {
            'air__temperature': np.empty(self._shape),
            'air__density': np.empty(self._shape),
        }


class EarthPort(EmptyPort):
    _name = 'earth_port'
    def __init__(self):
        EmptyPort.__init__(self)
        self._values = {
            'earth_surface__temperature': np.empty(self._shape),
            'earth_surface__density': np.empty(self._shape),
            'glacier_top_surface__slope': np.empty(self._shape),
        }


_SERVICES = {
    'air_port': AirPort(),
    'water_port': WaterPort(),
    'earth_port': EarthPort(),
}

_CLASSES = {
    'air_port': AirPort,
    'water_port': WaterPort,
    'earth_port': EarthPort,
}
_INSTANCES = {}
