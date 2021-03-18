import pytest

import numpy as np
from gimli import IncompatibleUnitsError, UnitNameError
from numpy.testing import assert_array_equal

from pymt.framework.bmi_bridge import BmiTimeInterpolator, GridMapperMixIn, _BmiCap


class SimpleBmi:
    def get_output_var_names(self):
        return ("elevation",)

    def get_var_grid(self, name):
        return 0

    def get_var_units(self, name):
        return "m"

    def get_var_type(self, name):
        return "float"

    def get_var_location(self, name):
        return "node"

    def get_var_nbytes(self, name):
        return self.get_var_itemsize(name) * 4

    def get_var_itemsize(self, name):
        return np.dtype("float").itemsize

    def get_value(self, name, out):
        out[:] = [1, 2, 3, 4]

    def get_grid_node_count(self, grid):
        return 4


class Bmi(GridMapperMixIn, _BmiCap, BmiTimeInterpolator):
    _cls = SimpleBmi


def test_value_wrap():
    """Test wrapping BMI time methods."""
    bmi = Bmi()

    assert bmi.var_units("elevation") == "m"
    assert_array_equal(bmi.get_value("elevation"), [1, 2, 3, 4])


def test_unit_conversion():
    """Test wrapping BMI time methods."""
    bmi = Bmi()

    assert_array_equal(bmi.get_value("elevation", units=None), [1.0, 2.0, 3.0, 4.0])
    assert_array_equal(bmi.get_value("elevation", units="m"), [1.0, 2.0, 3.0, 4.0])
    assert_array_equal(
        bmi.get_value("elevation", units="km"), [0.001, 0.002, 0.003, 0.004]
    )
    assert_array_equal(
        bmi.get_value("elevation", units="m2 km-1"), [1000.0, 2000.0, 3000.0, 4000.0]
    )


def test_incompatible_units():
    """Test wrapping BMI time methods."""
    bmi = Bmi()
    with pytest.raises(IncompatibleUnitsError):
        bmi.get_value("elevation", units="kg")


def test_bad_units():
    """Test wrapping BMI time methods."""
    bmi = Bmi()
    with pytest.raises(UnitNameError):
        bmi.get_value("elevation", units="not_real_units")
