import os

import numpy as np
from numpy.testing import assert_array_almost_equal
from nose.tools import assert_equal, assert_list_equal, assert_raises

from cmt.component.grid import GridMixIn


class Port(object):
    def get_component_name(self):
        return 'test-component'

    def get_input_item_count(self):
        return 1

    def get_input_item_list(self):
        return ['invar']

    def get_output_item_count(self):
        return 1

    def get_output_item_list(self):
        return ['outvar']


def test_raster_1d():
    class RasterPort(Port):
        def get_grid_shape(self, name):
            return (3, )

        def get_grid_spacing(self, name):
            return (2., )

        def get_grid_origin(self, name):
            return (3., )

    class Component(GridMixIn):
        def __init__(self):
            self._port = RasterPort()
            super(Component, self).__init__()

    c = Component()
    assert_array_almost_equal(c.get_x('invar'),
                              np.array([ 3.,  5.,  7.]))


def test_raster_2d():
    class RasterPort(Port):
        def get_grid_shape(self, name):
            return (2, 3)

        def get_grid_spacing(self, name):
            return (2., 1.)

        def get_grid_origin(self, name):
            return (0., 0.)

    class Component(GridMixIn):
        def __init__(self):
            self._port = RasterPort()
            super(Component, self).__init__()

    c = Component()
    assert_equal(c.name, 'test-component')
    assert_list_equal(c.input_items, ['invar'])
    assert_list_equal(c.output_items, ['outvar'])
    assert_equal(c.get_grid_type('invar'), 'RASTER')
    assert_array_almost_equal(c.get_x('invar'),
                              np.array([[ 0.,  1.,  2.], [ 0.,  1.,  2.]]))
    assert_array_almost_equal(c.get_y('invar'),
                              np.array([[ 0.,  0.,  0.], [ 2.,  2.,  2.]]))
    assert_array_almost_equal(c.get_connectivity('invar'),
                              np.array([0, 1, 4, 3, 1, 2, 5, 4]))
    assert_array_almost_equal(c.get_offset('invar'),
                              np.array([4, 8]))


def test_raster_3d():
    class RasterPort(Port):
        def get_grid_shape(self, name):
            return (2, 2, 3)

        def get_grid_spacing(self, name):
            return (1., 2., 1.)

        def get_grid_origin(self, name):
            return (0., 0., 0.)

    class Component(GridMixIn):
        def __init__(self):
            self._port = RasterPort()
            super(Component, self).__init__()

    c = Component()
    assert_array_almost_equal(c.get_x('invar'),
                              np.array([[[ 0.,  1.,  2.], [ 0.,  1.,  2.]],
                                        [[ 0.,  1.,  2.], [ 0.,  1.,  2.]]]))
    assert_array_almost_equal(c.get_y('invar'),
                              np.array([[[ 0.,  0.,  0.], [ 2.,  2.,  2.]],
                                        [[ 0.,  0.,  0.], [ 2.,  2.,  2.]]]))
    assert_array_almost_equal(c.get_z('invar'),
                              np.array([[[ 0.,  0.,  0.], [ 0.,  0.,  0.]],
                                        [[ 1.,  1.,  1.], [ 1.,  1.,  1.]]]))


def test_rectilinear():
    class RectilinearPort(Port):
        def get_grid_shape(self, name):
            return (2, 3)

        def get_grid_x(self, name):
            return (0., 3., 4)

        def get_grid_y(self, name):
            return (2., 7.)

    class Component(GridMixIn):
        def __init__(self):
            self._port = RectilinearPort()
            super(Component, self).__init__()

    c = Component()
    assert_equal(c.name, 'test-component')
    assert_list_equal(c.input_items, ['invar'])
    assert_list_equal(c.output_items, ['outvar'])
    assert_equal(c.get_grid_type('invar'), 'RECTILINEAR')
    assert_array_almost_equal(c.get_x('invar'),
                              np.array([[ 0.,  3.,  4.], [ 0.,  3.,  4.]]))
    assert_array_almost_equal(c.get_y('invar'),
                              np.array([[ 2.,  2.,  2.], [ 7.,  7.,  7.]]))


def test_structured():
    class StructuredPort(Port):
        def get_grid_shape(self, name):
            return (2, 3)

        def get_grid_x(self, name):
            return np.array([0., 1., 2., 0., 1., 2.])

        def get_grid_y(self, name):
            return np.array([0., 1., 2., 1., 2., 3.])

    class Component(GridMixIn):
        def __init__(self):
            self._port = StructuredPort()
            super(Component, self).__init__()

    c = Component()
    assert_equal(c.name, 'test-component')
    assert_list_equal(c.input_items, ['invar'])
    assert_list_equal(c.output_items, ['outvar'])
    assert_equal(c.get_grid_type('invar'), 'STRUCTURED')
    assert_array_almost_equal(c.get_x('invar'),
                              np.array([0., 1., 2., 0., 1., 2.]))
    assert_array_almost_equal(c.get_y('invar'),
                              np.array([0., 1., 2., 1., 2., 3.]))


def test_unstructured():
    class UnstructuredPort(Port):
        def get_grid_x(self, name):
            return np.array([0., 1., 0., 1., 2.])

        def get_grid_y(self, name):
            return np.array([0., 0., 1., 1., 0.])

        def get_grid_connectivity(self, name):
            return np.array([0, 1, 3, 2, 4, 3, 1])

        def get_grid_offset(self, name):
            return np.array([4, 7])

    class Component(GridMixIn):
        def __init__(self):
            self._port = UnstructuredPort()
            super(Component, self).__init__()

    c = Component()
    assert_equal(c.name, 'test-component')
    assert_list_equal(c.input_items, ['invar'])
    assert_list_equal(c.output_items, ['outvar'])
    assert_equal(c.get_grid_type('invar'), 'UNSTRUCTURED')
    assert_array_almost_equal(c.get_x('invar'),
                              np.array([0., 1., 0., 1., 2.]))
    assert_array_almost_equal(c.get_y('invar'),
                              np.array([0., 0., 1., 1., 0.]))


def test_get_grid_shape_is_none():
    class UnstructuredPort(Port):
        def get_grid_shape(self, name):
            return None

        def get_grid_x(self, name):
            return np.array([0., 1., 2.])

    class Component(GridMixIn):
        def __init__(self):
            self._port = UnstructuredPort()
            super(Component, self).__init__()

    c = Component()
    assert_equal(c.get_grid_type('invar'), 'UNSTRUCTURED')


def test_get_grid_shape_raises():
    class UnstructuredPort(Port):
        def get_grid_shape(self, name):
            raise NotImplementedError('get_grid_shape')

        def get_grid_x(self, name):
            return np.array([0., 1., 2.])

    class Component(GridMixIn):
        def __init__(self):
            self._port = UnstructuredPort()
            super(Component, self).__init__()

    c = Component()
    assert_equal(c.get_grid_type('invar'), 'UNSTRUCTURED')


def test_structured_1d():
    class RectilinearPort(Port):
        def get_grid_shape(self, name):
            return (2, 3)

        def get_grid_x(self, name):
            return np.array([0., 1., 2.])

        def get_grid_y(self, name):
            return np.array([0., 1.])

        def get_grid_z(self, name):
            raise NotImplementedError('get_grid_z')

    class Component(GridMixIn):
        def __init__(self):
            self._port = RectilinearPort()
            super(Component, self).__init__()

    c = Component()
    assert_equal(c.get_grid_type('invar'), 'RECTILINEAR')
    assert_equal(c.get_grid_type('outvar'), 'RECTILINEAR')
    with assert_raises(IndexError):
        c.get_z('invar')
