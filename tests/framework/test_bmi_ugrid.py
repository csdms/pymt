"""Unit tests for the pymt.framwork.bmi_ugrid module."""
import xarray as xr
import numpy as np

from pymt.framework.bmi_ugrid import Scalar, Vector, Points, Unstructured
from pymt.framework.bmi_bridge import _BmiCap


grid_id = 0


class TestScalar:

    def get_grid_rank(self, grid_id):
        return 0


class ScalarBmi(_BmiCap):
    _cls = TestScalar


def test_scalar_grid():
    """Test creating a scalar grid."""
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
    """Test creating a vector grid."""
    bmi = VectorBmi()
    grid = Vector(bmi, grid_id)

    assert grid.ndim == 1
    assert grid.metadata["type"] == "vector"
    assert grid.data_vars["mesh"].attrs["type"] == "vector"
    assert isinstance(grid, xr.Dataset)


class TestPoints:

    x = np.array([0, 1, 0, 1])
    y = np.array([0, 0, 1, 1])
    node_count = x.size

    def get_grid_rank(self, grid_id):
        return 2

    def get_grid_node_count(self, grid_id):
        return self.node_count

    def get_grid_x(self, grid_id, out=None):
        return self.x

    def get_grid_y(self, grid_id, out=None):
        return self.y


class PointsBmi(_BmiCap):
    _cls = TestPoints


def test_points_grid():
    """Test creating a grid from points."""
    bmi = PointsBmi()
    grid = Points(bmi, grid_id)

    assert isinstance(grid, xr.Dataset)
    assert grid.ndim == 2
    assert grid.metadata["type"] == "points"
    assert grid.data_vars["mesh"].attrs["type"] == "points"
    assert type(grid.data_vars["node_x"].data) == np.ndarray


class TestUnstructured(TestPoints):

    def get_grid_number_of_faces(self, grid_id):
        return 1

    def get_grid_nodes_per_face(self, grid_id, out=None):
        return 4

    def get_grid_face_nodes(self, grid_id, out=None):
        return np.array([0, 1, 3, 2])


class UnstructuredBmi(_BmiCap):
    _cls = TestUnstructured


def test_unstructured_grid():
    """Test creating an unstructured grid."""
    bmi = UnstructuredBmi()
    grid = Unstructured(bmi, grid_id)

    assert isinstance(grid, xr.Dataset)
    assert grid.ndim == 2
    assert grid.metadata["type"] == "unstructured"
    assert grid.data_vars["mesh"].attrs["type"] == "unstructured"
    assert type(grid.data_vars["node_x"].data) == np.ndarray
