#! /usr/bin/env python import unittest

import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal
from nose.tools import assert_equal, assert_raises, assert_is

try:    
    import ESMF
except ImportError:
    _WITH_ESMF = False
else:
    _WITH_ESMF = True
    from cmt.grids.esmp import (EsmpRasterField, EsmpRectilinear,
                                EsmpStructured, EsmpUnstructured,
                                EsmpUniformRectilinear, EsmpRectilinearField,
                                DimensionError)
    from cmt.grids.esmp import run_regridding


def setup():
    ESMF.Manager()


def test_2d():
    # Create a grids that looks like this,
    #
    #
    #    (0) --- (1) --- (2)
    #     |       |       |
    #     |   0   |   1   |
    #     |       |       |
    #    (3) --- (4) --- (5)

    g = EsmpUnstructured([0, 1, 2, 0, 1, 2], [0, 0, 0, 1, 1, 1],
                         [0, 1, 4, 3, 1, 2, 5, 4], [4, 8])
    g = EsmpStructured([0, 1, 2, 0, 1, 2], [0, 0, 0, 1, 1, 1], (3, 2))

    # The as_mesh method provides a view of the grid as an ESMP_Mesh.

    assert_equal(g.as_mesh().element_count, 2)
    assert_equal(g.as_mesh().node_count, 6)

    # ESMF elements are the same as the grids cells. Likewise with
    # nodes and points.
    g = EsmpRectilinear([0, 1, 2], [0, 1])
    assert_equal(g.as_mesh().element_count, g.get_cell_count())
    assert_equal(g.as_mesh().node_count, g.get_point_count())

    g = EsmpUniformRectilinear([3, 2], [1., 1.], [0., 0.])


def test_raster():
    # Create a grids that looks like this,
    #
    #
    #    (0) --- (1) --- (2)
    #     |       |       |
    #     |   0   |   1   |
    #     |       |       |
    #    (3) --- (4) --- (5)

    # Create the field,

    g = EsmpRasterField((2, 3), (1, 2), (0, 0))
    assert_equal(g.get_cell_count(), 2)
    assert_equal(g.get_point_count(), 6)

    # Add some data at the points of our grid.

    data = np.arange(6)
    g.add_field('var0', data, centering='point')
    assert_array_equal(g.get_field('var0').data,
                       np.array([0., 1., 2., 3., 4., 5.], dtype=np.float64))

    data = np.arange(6)
    data.shape = (2, 3)
    g.add_field('var0', data, centering='point')
    assert_array_equal(g.get_field('var0').data,
                       np.array([0., 1., 2., 3., 4., 5.], dtype=np.float64))

    # If the size or shape doesn't match, it's an error.

    # DimensionError: 2 != 6
    data = np.arange(2)
    with assert_raises(DimensionError):
        g.add_field('bad var', data, centering='point')

    # DimensionError: (3, 2) != (2, 3)
    data = np.ones((3, 2))
    with assert_raises(DimensionError):
        g.add_field('bad var', data, centering='point')


def test_mapper():
    src = EsmpRasterField((3, 3), (1, 1), (0, 0))
    data = np.arange(src.get_cell_count(), dtype=np.float64)
    src.add_field('srcfield', data, centering='zonal')

    assert_equal(src.get_point_count(), 9)
    assert_equal(src.get_cell_count(), 4)

    assert_array_equal(src.get_x(),
                       np.array([0., 1., 2., 0., 1., 2., 0., 1., 2.]))
    assert_array_equal(src.get_y(),
                       np.array([0., 0., 0., 1., 1., 1., 2., 2., 2.]))

    assert_array_equal(src.get_connectivity(),
                       np.array(
                           [0, 1, 4, 3, 1, 2, 5, 4, 3, 4, 7, 6, 4, 5, 8, 7]))

    dst = EsmpRectilinearField([0., .5, 1.5, 2.], [0., .5, 1.5, 2.])
    data = np.empty(dst.get_cell_count(), dtype=np.float64)
    dst.add_field('dstfield', data, centering='zonal')

    assert_equal(dst.get_point_count(), 16)
    assert_equal(dst.get_cell_count(), 9)

    assert_array_equal(dst.get_x(),
                       np.array([0., 0.5, 1.5, 2.,
                                 0., 0.5, 1.5, 2.,
                                 0., 0.5, 1.5, 2.,
                                 0., 0.5, 1.5, 2.]))
    assert_array_equal(dst.get_y(),
                       np.array([0., 0., 0., 0.,
                                 0.5, 0.5, 0.5, 0.5,
                                 1.5, 1.5, 1.5, 1.5,
                                 2., 2., 2., 2.]))
    assert_array_equal(dst.get_connectivity(),
                       np.array([0,  1,  5,  4, 1,  2,  6,  5,  2,  3,  7,  6,
                                 4,  5,  9,  8, 5,  6, 10,  9,  6,  7, 11, 10,
                                 8,  9, 13, 12, 9, 10, 14, 13, 10, 11, 15, 14]))

    src_field = src.as_esmp('srcfield')
    dst_field = dst.as_esmp('dstfield')

    assert_equal(src.as_mesh().element_count, 4)
    assert_equal(src.as_mesh().node_count, 9)

    assert_equal(dst.as_mesh().element_count, 9)
    assert_equal(dst.as_mesh().node_count, 16)

    f = run_regridding(src_field, dst_field)
    assert_is(f, dst_field)


def test_values_on_cells():
    (n_rows, n_cols) = (300, 300)
    src = EsmpRasterField((n_rows, n_cols), (1, 1), (0, 0))

    (x, y) = np.meshgrid(np.arange(0.5, 299.5, 1.),
                         np.arange(0.5, 299.5, 1.))

    data = np.sin(np.sqrt(x ** 2 + y ** 2) * np.pi / n_rows)
    src.add_field('srcfield', data, centering='zonal')

    dst = EsmpRasterField((n_rows * 2 - 1, n_cols * 2 - 1), (1. / 2, 1. / 2),
                          (0, 0))
    data = np.empty(dst.get_cell_count(), dtype=np.float64)
    dst.add_field('dstfield', data, centering='zonal')

    src_field = src.as_esmp('srcfield')
    dst_field = dst.as_esmp('dstfield')

    f = run_regridding(src_field, dst_field)
    assert_is(f, dst_field)

    (x, y) = np.meshgrid(np.arange(0.5, 299.5, .5),
                         np.arange(0.5, 299.5, .5))
    exact = np.sin(np.sqrt(x ** 2 + y ** 2) * np.pi / n_rows)
    residual = np.abs(exact.flat - f.data)/(n_rows * n_cols * 4.)
    assert_array_almost_equal(residual, np.zeros_like(residual))


def test_values_on_points():
    (n_rows, n_cols) = (300, 300)
    src = EsmpRasterField((n_rows, n_cols), (1, 1), (0, 0))

    (x, y) = np.meshgrid(np.arange(0.5, 300.5, 1.),
                         np.arange(0.5, 300.5, 1.))
    data = np.sin(np.sqrt(x ** 2 + y ** 2) * np.pi / n_rows)
    src.add_field('srcfield_at_points', data, centering='point')

    dst = EsmpRasterField((n_rows * 2 - 1, n_cols * 2 - 1), (1. / 2, 1. / 2),
                          (0, 0))
    data = np.empty(dst.get_point_count(), dtype=np.float64)
    dst.add_field('dstfield_at_points', data, centering='point')

    src_field = src.as_esmp('srcfield_at_points')
    dst_field = dst.as_esmp('dstfield_at_points')

    f = run_regridding(src_field, dst_field,
                       method=ESMF.RegridMethod.BILINEAR)

    (x, y) = np.meshgrid(np.arange(0.5, 300., .5),
                         np.arange(0.5, 300., .5))
    exact = np.sin(np.sqrt(x ** 2 + y ** 2) * np.pi / n_rows)
    residual = np.abs(exact.flat - f.data)/(n_rows * n_cols * 4.)
    assert_array_almost_equal(residual, np.zeros_like(residual))
