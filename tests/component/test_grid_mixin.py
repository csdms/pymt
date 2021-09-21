import numpy as np
import pytest
from pytest import approx

from pymt.component.grid import GridMixIn


class Port:
    def __init__(self, name, uses=None, provides=None):
        self._name = name
        self._uses = uses or []
        self._provides = provides or []

    def get_component_name(self):
        return self._name

    def get_input_item_count(self):
        return len(self._uses)

    def get_input_item_list(self):
        return self._uses

    def get_output_item_count(self):
        return len(self._provides)

    def get_output_item_list(self):
        return self._provides


def test_exchange_items():
    class Component(GridMixIn):
        def __init__(self):
            self._port = Port("test", uses=["invar"], provides=["outvar"])
            super().__init__()

    c = Component()
    assert c.input_items == ["invar"]
    assert c.output_items == ["outvar"]


def test_no_exchange_items():
    class Component(GridMixIn):
        def __init__(self):
            self._port = Port("test")
            super().__init__()

    c = Component()
    assert c.input_items == []
    assert c.output_items == []


def test_raster_1d():
    class RasterPort(Port):
        def get_grid_shape(self, grid_id):
            return (3,)

        def get_grid_spacing(self, grid_id):
            return (2.0,)

        def get_grid_origin(self, grid_id):
            return (3.0,)

    class Component(GridMixIn):
        def __init__(self):
            self._port = RasterPort("test", uses=["invar"])
            super().__init__()

    c = Component()
    assert c.get_x("invar") == approx(np.array([3.0, 5.0, 7.0]))


def test_raster_2d():
    class RasterPort(Port):
        def get_grid_shape(self, grid_id):
            return (2, 3)

        def get_grid_spacing(self, grid_id):
            return (2.0, 1.0)

        def get_grid_origin(self, grid_id):
            return (0.0, 0.0)

    class Component(GridMixIn):
        def __init__(self):
            self._port = RasterPort("test-2d", uses=["invar"], provides=["outvar"])
            super().__init__()

    c = Component()
    assert c.name == "test-2d"
    assert c.get_grid_type(0) == "RASTER"
    assert c.get_x(0) == approx(np.array([[0.0, 1.0, 2.0], [0.0, 1.0, 2.0]]))
    assert c.get_y(0) == approx(np.array([[0.0, 0.0, 0.0], [2.0, 2.0, 2.0]]))
    assert np.all(c.get_connectivity(0) == np.array([0, 1, 4, 3, 1, 2, 5, 4]))
    assert np.all(c.get_offset(0) == np.array([4, 8]))


def test_raster_3d():
    class RasterPort(Port):
        def get_grid_shape(self, grid_id):
            return (2, 2, 3)

        def get_grid_spacing(self, grid_id):
            return (1.0, 2.0, 1.0)

        def get_grid_origin(self, grid_id):
            return (0.0, 0.0, 0.0)

    class Component(GridMixIn):
        def __init__(self):
            self._port = RasterPort("test-3d", uses=["invar"])
            super().__init__()

    c = Component()
    assert c.get_x(0) == approx(
        np.array(
            [[[0.0, 1.0, 2.0], [0.0, 1.0, 2.0]], [[0.0, 1.0, 2.0], [0.0, 1.0, 2.0]]]
        )
    )
    assert c.get_y(0) == approx(
        np.array(
            [[[0.0, 0.0, 0.0], [2.0, 2.0, 2.0]], [[0.0, 0.0, 0.0], [2.0, 2.0, 2.0]]]
        )
    )
    assert c.get_z(0) == approx(
        np.array(
            [[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]]
        )
    )


def test_rectilinear():
    class RectilinearPort(Port):
        def get_grid_shape(self, grid_id):
            return (2, 3)

        def get_grid_x(self, grid_id):
            return (0.0, 3.0, 4)

        def get_grid_y(self, grid_id):
            return (2.0, 7.0)

    class Component(GridMixIn):
        def __init__(self):
            self._port = RectilinearPort("test", uses=["invar"])
            super().__init__()

    c = Component()
    assert c.get_grid_type(0) == "RECTILINEAR"
    assert c.get_x(0) == approx(np.array([[0.0, 3.0, 4.0], [0.0, 3.0, 4.0]]))
    assert c.get_y(0) == approx(np.array([[2.0, 2.0, 2.0], [7.0, 7.0, 7.0]]))


def test_structured():
    class StructuredPort(Port):
        def get_grid_shape(self, grid_id):
            return (2, 3)

        def get_grid_x(self, grid_id):
            return np.array([0.0, 1.0, 2.0, 0.0, 1.0, 2.0])

        def get_grid_y(self, grid_id):
            return np.array([0.0, 1.0, 2.0, 1.0, 2.0, 3.0])

    class Component(GridMixIn):
        def __init__(self):
            self._port = StructuredPort("test", uses=["invar"])
            super().__init__()

    c = Component()
    assert c.get_grid_type(0) == "STRUCTURED"
    assert c.get_x(0) == approx(np.array([0.0, 1.0, 2.0, 0.0, 1.0, 2.0]))
    assert c.get_y(0) == approx(np.array([0.0, 1.0, 2.0, 1.0, 2.0, 3.0]))


def test_unstructured():
    class UnstructuredPort(Port):
        def get_grid_x(self, grid_id):
            return np.array([0.0, 1.0, 0.0, 1.0, 2.0])

        def get_grid_y(self, grid_id):
            return np.array([0.0, 0.0, 1.0, 1.0, 0.0])

        def get_grid_connectivity(self, grid_id):
            return np.array([0, 1, 3, 2, 4, 3, 1])

        def get_grid_offset(self, grid_id):
            return np.array([4, 7])

    class Component(GridMixIn):
        def __init__(self):
            self._port = UnstructuredPort("test", uses=["invar"])
            super().__init__()

    c = Component()
    assert c.get_grid_type(0) == "UNSTRUCTURED"
    assert c.get_x(0) == approx(np.array([0.0, 1.0, 0.0, 1.0, 2.0]))
    assert c.get_y(0) == approx(np.array([0.0, 0.0, 1.0, 1.0, 0.0]))


def test_get_grid_shape_is_none():
    class UnstructuredPort(Port):
        def get_grid_shape(self, grid_id):
            return None

        def get_grid_x(self, grid_id):
            return np.array([0.0, 1.0, 2.0])

    class Component(GridMixIn):
        def __init__(self):
            self._port = UnstructuredPort("test", uses=["invar"])
            super().__init__()

    c = Component()
    assert c.get_grid_type(0) == "UNSTRUCTURED"


def test_get_grid_shape_raises():
    class UnstructuredPort(Port):
        def get_grid_shape(self, grid_id):
            raise NotImplementedError("get_grid_shape")

        def get_grid_x(self, grid_id):
            return np.array([0.0, 1.0, 2.0])

    class Component(GridMixIn):
        def __init__(self):
            self._port = UnstructuredPort("test", uses=["invar"])
            super().__init__()

    c = Component()
    assert c.get_grid_type(0) == "UNSTRUCTURED"


def test_structured_1d():
    class RectilinearPort(Port):
        def get_grid_shape(self, grid_id):
            return (2, 3)

        def get_grid_x(self, grid_id):
            return np.array([0.0, 1.0, 2.0])

        def get_grid_y(self, grid_id):
            raise NotImplementedError("get_grid_y")

        def get_grid_z(self, grid_id):
            raise NotImplementedError("get_grid_z")

    class Component(GridMixIn):
        def __init__(self):
            self._port = RectilinearPort("test", uses=["invar"])
            super().__init__()

    c = Component()
    assert c.get_grid_type(0) == "RECTILINEAR"
    with pytest.raises(IndexError):
        c.get_z(0)
