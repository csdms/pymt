import numpy as np
from cfunits import Units


class UnitConverter(object):

    """Convert values in some units to another."""

    def __init__(self, from_units):
        self._units = Units(from_units)
        if not self._units.isvalid:
            raise ValueError("invalid units ({0})".format(from_units))

    @property
    def units(self):
        return str(self._units)

    def __call__(self, val, to_units):
        return self._convert(val, self._units, to_units)

    def inv(self, val, from_units):
        return self._convert(val, from_units, self._units)

    @staticmethod
    def _convert(val, from_units, to_units):
        from_units, to_units = Units(from_units), Units(to_units)
        if from_units.equals(to_units):
            return val
        else:
            return Units.conform(val, from_units, to_units)

    def __repr__(self):
        return "UnitConverter(\"{0}\")".format(str(self.from_units))


def transform_math_to_azimuth(angle, units="rad"):
    angle *= -1.0
    if units == "rad":
        angle += np.pi * 0.5
    else:
        angle += 90.0
    return angle


def transform_azimuth_to_math(angle, units="rad"):
    angle *= -1.0
    if units == "rad":
        angle += np.pi * 0.5
    else:
        angle += 90.0
    return angle
