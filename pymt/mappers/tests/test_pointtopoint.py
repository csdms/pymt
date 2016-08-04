#! /usr/bin/env python
import numpy as np
from numpy.testing import assert_array_almost_equal
from nose.tools import (assert_equal, assert_is, assert_true, assert_false,
                        assert_is_instance, assert_raises)

from cmt.grids.map import RectilinearMap as Rectilinear
from cmt.mappers import find_mapper, NearestVal


def test_all_good():
    src = Rectilinear([0, 1, 2], [0, 2])
    dst = Rectilinear([.5, 1.5, 2.5], [.25, 1.25])

    src_vals = np.arange(src.get_point_count ())

    mapper = NearestVal()
    mapper.initialize(dst, src)
    dst_vals = mapper.run(src_vals)

    assert_array_almost_equal(dst_vals, np.array([0., 1., 2., 3., 4., 5.]))


def test_some_bad():
    src = Rectilinear([0, 1, 2], [0, 2])
    dst = Rectilinear([.5, 1.5, 2.5], [.25, 1.25])

    mapper = NearestVal()
    mapper.initialize(dst, src)

    src_vals = np.arange(src.get_point_count())
    src_vals[2] = -999
    dst_vals = np.zeros(dst.get_point_count()) - 1
    rv = mapper.run(src_vals, dst_vals)

    assert_is(rv, dst_vals)
    assert_array_almost_equal(dst_vals, np.array([0., 1., -1., 3., 4., 5.]))


def test_no_destination():
    src = Rectilinear([0, 1, 2], [0, 2])
    dst = Rectilinear([.5, 1.5, 2.5], [.25, 1.25])

    mapper = NearestVal()
    mapper.initialize(dst, src)

    src_vals = np.arange(src.get_point_count())
    dst_vals = mapper.run(src_vals)
    assert_array_almost_equal(dst_vals, np.array([0., 1., 2., 3., 4., 5.]))


def test_destination_init_zero():
    src = Rectilinear([0, 1, 2], [0, 2])
    dst = Rectilinear([.5, 1.5, 2.5], [.25, 1.25])

    mapper = NearestVal()
    mapper.initialize(dst, src)

    src_vals = np.arange(src.get_point_count())
    src_vals[2] = -999
    dst_vals = mapper.run(src_vals)
    assert_array_almost_equal(dst_vals, np.array([0., 1., 0., 3., 4., 5.]))


def test_bad_destination():
    src = Rectilinear([0, 1, 2], [0, 2])
    dst = Rectilinear([.5, 1.5, 2.5], [.25, 1.25])

    mapper = NearestVal()
    mapper.initialize(dst, src)

    src_vals = np.arange(src.get_point_count())
    dst_vals = [0.] * src.get_point_count()
    with assert_raises(TypeError):
        mapper.run(src_vals, dst_vals)


def test_find_mapper():
    src = Rectilinear([0, 1, 2], [0, 2])
    dst = Rectilinear([.5, 1.5, 2.5], [.25, 1.25])

    mappers = find_mapper(dst, src)
    assert_equal(len(mappers), 3)
    assert_equal(mappers[0].name(), 'PointToPoint')
    assert_is_instance(mappers[0], NearestVal)


def test_incompatible_grids():
    grid = Rectilinear([0, 1, 2], [0, 2])

    mapper = NearestVal()

    assert_false(mapper.test(grid, None))
    assert_false(mapper.test(None, grid))
    assert_true(mapper.test(grid, grid))
