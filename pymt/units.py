import numpy as np
from cfunits import Units


class UnitConverter(object):

    """Convert values in some units to another."""

    def __init__(self, from_units):
        self._from_units = Units(from_units)

    def __call__(self, time, units):
        to_units = Units(units)
        if self._from_units.equals(to_units):
            return time
        else:
            return Units.conform(time, self._from_units, to_units)


def transform_math_to_azimuth(angle, units):
    angle *= -1.0
    if units == Units("rad"):
        angle += np.pi * 0.5
    else:
        angle += 90.0


def transform_azimuth_to_math(angle, units):
    angle *= -1.0
    if units == Units("rad"):
        angle -= np.pi * 0.5
    else:
        angle -= 90.0
