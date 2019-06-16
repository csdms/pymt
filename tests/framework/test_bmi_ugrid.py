"""Unit tests for the pymt.framwork.bmi_ugrid module."""
import xarray as xr

from pymt.framework.bmi_ugrid import Scalar, Vector
from pymt.framework.bmi_bridge import _BmiCap


grid_id = 0


class TestScalar:

    def get_grid_rank(self, grid_id):
        return 0


class ScalarBmi(_BmiCap):
    _cls = TestScalar


def test_scalar_grid():
    """Testing creating a scalar grid."""
    bmi = ScalarBmi()
    grid = Scalar(bmi, grid_id)

    assert grid.ndim == 0
    assert grid.metadata["type"] == "scalar"
    assert grid.data_vars["mesh"].attrs["type"] == "scalar"
    assert isinstance(grid, xr.Dataset)


class TestVector:

    def get_grid_rank(self, grid_id):
        return 1


class VectorBmi(_BmiCap):
    _cls = TestVector


def test_vector_grid():
    """Testing creating a vector grid."""
    bmi = VectorBmi()
    grid = Vector(bmi, grid_id)

    assert grid.ndim == 1
    assert grid.metadata["type"] == "vector"
    assert grid.data_vars["mesh"].attrs["type"] == "vector"
    assert isinstance(grid, xr.Dataset)
