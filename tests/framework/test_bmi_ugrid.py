"""Unit tests for the pymt.framwork.bmi_ugrid module."""

import numpy as np
import xarray as xr

from pymt.framework.bmi_ugrid import (
    Points,
    Rectilinear,
    Scalar,
    StructuredQuadrilateral,
    UniformRectilinear,
    Unstructured,
    Vector,
)

grid_id = 0


class BmiScalar:
    def grid_type(self, grid_id):
        return "scalar"

    def grid_ndim(self, grid_id):
        return 0


def test_scalar_grid():
    """Test creating a scalar grid."""
    bmi = BmiScalar()
    grid = Scalar(bmi, grid_id)

    assert grid.ndim == 0
    assert grid.metadata["type"] == bmi.grid_type(grid_id)
    assert grid.data_vars["mesh"].attrs["type"] == bmi.grid_type(grid_id)
    assert isinstance(grid, xr.Dataset)


class BmiVector:
    def grid_type(self, grid_id):
        return "vector"

    def grid_ndim(self, grid_id):
        return 1


def test_vector_grid():
    """Test creating a vector grid."""
    bmi = BmiVector()
    grid = Vector(bmi, grid_id)

    assert grid.ndim == 1
    assert grid.metadata["type"] == bmi.grid_type(grid_id)
    assert grid.data_vars["mesh"].attrs["type"] == bmi.grid_type(grid_id)
    assert isinstance(grid, xr.Dataset)


class BmiPoints:
    x = np.array([0.0, 1.0, 0.0, 1.0])
    y = np.array([0.0, 0.0, 1.0, 1.0])

    def grid_type(self, grid_id):
        return "points"

    def grid_ndim(self, grid_id):
        return 2

    def grid_x(self, grid_id, out=None):
        return self.x.flatten()

    def grid_y(self, grid_id, out=None):
        return self.y.flatten()


def test_points_grid():
    """Test creating a grid from points."""
    bmi = BmiPoints()
    grid = Points(bmi, grid_id)

    assert isinstance(grid, xr.Dataset)
    assert grid.ndim == 2
    assert grid.metadata["type"] == bmi.grid_type(grid_id)
    assert grid.data_vars["mesh"].attrs["type"] is bmi.grid_type(grid_id)
    assert type(grid.data_vars["node_x"].data) is np.ndarray


class BmiUnstructured(BmiPoints):
    def grid_type(self, grid_id):
        return "unstructured"

    def grid_nodes_per_face(self, grid_id, out=None):
        return 4

    def grid_face_nodes(self, grid_id, out=None):
        return np.array([0, 1, 3, 2])

    def grid_face_node_offset(self, grid_id, out=None):
        nodes_per_face = self.grid_nodes_per_face(grid_id)
        return np.cumsum(nodes_per_face)


def test_unstructured_grid():
    """Test creating an unstructured grid."""
    bmi = BmiUnstructured()
    grid = Unstructured(bmi, grid_id)

    assert isinstance(grid, xr.Dataset)
    assert grid.ndim == 2
    assert grid.metadata["type"] == bmi.grid_type(grid_id)
    assert grid.data_vars["mesh"].attrs["type"] is bmi.grid_type(grid_id)
    assert type(grid.data_vars["node_x"].data) is np.ndarray


class BmiStructuredQuadrilateral:
    x = np.array([[0.0, 3.0], [1.0, 4.0], [2.0, 5.0]])
    y = np.array([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0]])

    def grid_type(self, grid_id):
        return "structured_quadrilateral"

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
    bmi = BmiStructuredQuadrilateral()
    grid = StructuredQuadrilateral(bmi, grid_id)

    assert isinstance(grid, xr.Dataset)
    assert grid.ndim == 2
    assert grid.metadata["type"] == bmi.grid_type(grid_id)
    assert grid.data_vars["mesh"].attrs["type"] is bmi.grid_type(grid_id)
    assert type(grid.data_vars["node_x"].data) is np.ndarray


class BmiRectilinear:
    x = np.array([1, 4, 8])
    y = np.array([0, 1, 2, 3])
    shape = (len(y), len(x))

    def grid_type(self, grid_id):
        return "rectilinear"

    def grid_ndim(self, grid_id):
        return len(self.shape)

    def grid_shape(self, grid_id, out=None):
        return np.array(self.shape)

    def grid_x(self, grid_id, out=None):
        return self.x

    def grid_y(self, grid_id, out=None):
        return self.y


def test_rectilinear_grid():
    """Test creating a rectilinear grid."""
    bmi = BmiRectilinear()
    grid = Rectilinear(bmi, grid_id)

    assert isinstance(grid, xr.Dataset)
    assert grid.ndim == 2
    assert grid.metadata["type"] == bmi.grid_type(grid_id)
    assert grid.data_vars["mesh"].attrs["type"] is bmi.grid_type(grid_id)
    assert type(grid.data_vars["node_x"].data) is np.ndarray


class BmiRectilinear3D:
    x = np.array([1, 4, 8])
    y = np.array([0, 1, 2, 3])
    z = np.array([-2, 0, 1])
    shape = (len(z), len(y), len(x))

    def grid_type(self, grid_id):
        return "rectilinear"

    def grid_ndim(self, grid_id):
        return len(self.shape)

    def grid_shape(self, grid_id, out=None):
        return np.array(self.shape)

    def grid_x(self, grid_id, out=None):
        return self.x

    def grid_y(self, grid_id, out=None):
        return self.y

    def grid_z(self, grid_id, out=None):
        return self.z


def test_rectilinear_grid_3d():
    """Test creating a 3D rectilinear grid."""
    bmi = BmiRectilinear3D()
    grid = Rectilinear(bmi, grid_id)

    assert isinstance(grid, xr.Dataset)
    assert grid.ndim == 3
    assert grid.metadata["type"] == bmi.grid_type(grid_id)
    assert grid.data_vars["mesh"].attrs["type"] is bmi.grid_type(grid_id)
    assert type(grid.data_vars["node_x"].data) is np.ndarray
    assert len(grid.data_vars["node_x"].data) == np.prod(bmi.grid_shape(grid_id))


class BmiUniformRectilinear:
    shape = (4, 3)
    spacing = (1.0, 1.0)
    origin = (5.0, 2.0)

    def grid_type(self, grid_id):
        return "uniform_rectilinear"

    def grid_ndim(self, grid_id):
        return len(self.shape)

    def grid_shape(self, grid_id, out=None):
        return np.array(self.shape)

    def grid_spacing(self, grid_id, out=None):
        return np.array(self.spacing)

    def grid_origin(self, grid_id, out=None):
        return np.array(self.origin)


def test_uniform_rectilinear_grid():
    """Test creating a uniform rectilinear grid."""
    bmi = BmiUniformRectilinear()
    grid = UniformRectilinear(bmi, grid_id)

    assert isinstance(grid, xr.Dataset)
    assert grid.ndim == 2
    assert grid.metadata["type"] == bmi.grid_type(grid_id)
    assert grid.data_vars["mesh"].attrs["type"] is bmi.grid_type(grid_id)
    assert type(grid.data_vars["node_x"].data) is np.ndarray
