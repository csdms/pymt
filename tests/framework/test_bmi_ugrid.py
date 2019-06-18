"""Unit tests for the pymt.framwork.bmi_ugrid module."""
import xarray as xr
import numpy as np

from pymt.framework.bmi_ugrid import (Scalar, Vector, Points,
                                      Unstructured, StructuredQuadrilateral)


grid_id = 0


class TestScalar:

    def grid_ndim(self, grid_id):
        return 0

def test_scalar_grid():
    """Test creating a scalar grid."""
    bmi = TestScalar()
    grid = Scalar(bmi, grid_id)

    assert grid.ndim == 0
    assert grid.metadata["type"] == "scalar"
    assert grid.data_vars["mesh"].attrs["type"] == "scalar"
    assert isinstance(grid, xr.Dataset)


class TestVector:

    def grid_ndim(self, grid_id):
        return 1


def test_vector_grid():
    """Test creating a vector grid."""
    bmi = TestVector()
    grid = Vector(bmi, grid_id)

    assert grid.ndim == 1
    assert grid.metadata["type"] == "vector"
    assert grid.data_vars["mesh"].attrs["type"] == "vector"
    assert isinstance(grid, xr.Dataset)


class TestPoints:

    x = np.array([0., 1., 0., 1.])
    y = np.array([0., 0., 1., 1.])

    def grid_ndim(self, grid_id):
        return 2

    def grid_x(self, grid_id, out=None):
        return self.x.flatten()

    def grid_y(self, grid_id, out=None):
        return self.y.flatten()


def test_points_grid():
    """Test creating a grid from points."""
    bmi = TestPoints()
    grid = Points(bmi, grid_id)

    assert isinstance(grid, xr.Dataset)
    assert grid.ndim == 2
    assert grid.metadata["type"] == "points"
    assert grid.data_vars["mesh"].attrs["type"] == "points"
    assert type(grid.data_vars["node_x"].data) == np.ndarray


class TestUnstructured(TestPoints):

    def grid_nodes_per_face(self, grid_id, out=None):
        return 4

    def grid_face_nodes(self, grid_id, out=None):
        return np.array([0, 1, 3, 2])

    def grid_face_node_offset(self, grid_id, out=None):
        nodes_per_face = self.grid_nodes_per_face(grid_id)
        return np.cumsum(nodes_per_face)


def test_unstructured_grid():
    """Test creating an unstructured grid."""
    bmi = TestUnstructured()
    grid = Unstructured(bmi, grid_id)

    assert isinstance(grid, xr.Dataset)
    assert grid.ndim == 2
    assert grid.metadata["type"] == "unstructured"
    assert grid.data_vars["mesh"].attrs["type"] == "unstructured"
    assert type(grid.data_vars["node_x"].data) == np.ndarray


class TestStructuredQuadrilateral():

    x = np.array([[0.,3.], [1.,4.], [2.,5.]])
    y = np.array([[0.,1.], [2.,3.], [4.,5.]])

    def grid_ndim(self, grid_id):
        return self.x.ndim

    def grid_shape(self, grid_id, out=None):
        return np.array(self.x.shape)

    def grid_x(self, grid_id, out=None):
        return self.x.flatten()

    def grid_y(self, grid_id, out=None):
        return self.y.flatten()


def test_structured_quadrilateral_grid():
    """Test creating a structured quadrilateral grid."""
    bmi = TestStructuredQuadrilateral()
    grid = StructuredQuadrilateral(bmi, grid_id)

    assert isinstance(grid, xr.Dataset)
    assert grid.ndim == 2
    assert grid.metadata["type"] == "structured_quadrilateral"
    assert grid.data_vars["mesh"].attrs["type"] == "structured_quadrilateral"
    assert type(grid.data_vars["node_x"].data) == np.ndarray
