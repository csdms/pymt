#! /usr/bin/env python
import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal

from pymt.grids.map import RectilinearMap as Rectilinear
from pymt.mappers import NearestVal, find_mapper


def test_all_good():
    src = Rectilinear([0, 1, 2], [0, 2])
    dst = Rectilinear([0.5, 1.5, 2.5], [0.25, 1.25])

    src_vals = np.arange(src.get_point_count())

    mapper = NearestVal()
    mapper.initialize(dst, src)
    dst_vals = mapper.run(src_vals)

    assert_array_almost_equal(dst_vals, np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0]))


def test_some_bad():
    src = Rectilinear([0, 1, 2], [0, 2])
    dst = Rectilinear([0.5, 1.5, 2.5], [0.25, 1.25])

    mapper = NearestVal()
    mapper.initialize(dst, src)

    src_vals = np.arange(src.get_point_count())
    src_vals[2] = -999
    dst_vals = np.zeros(dst.get_point_count()) - 1
    rv = mapper.run(src_vals, dst_vals)

    assert rv is dst_vals
    assert_array_almost_equal(dst_vals, np.array([0.0, 1.0, -1.0, 3.0, 4.0, 5.0]))


def test_no_destination():
    src = Rectilinear([0, 1, 2], [0, 2])
    dst = Rectilinear([0.5, 1.5, 2.5], [0.25, 1.25])

    mapper = NearestVal()
    mapper.initialize(dst, src)

    src_vals = np.arange(src.get_point_count())
    dst_vals = mapper.run(src_vals)
    assert_array_almost_equal(dst_vals, np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0]))


def test_destination_init_zero():
    src = Rectilinear([0, 1, 2], [0, 2])
    dst = Rectilinear([0.5, 1.5, 2.5], [0.25, 1.25])

    mapper = NearestVal()
    mapper.initialize(dst, src)

    src_vals = np.arange(src.get_point_count())
    src_vals[2] = -999
    dst_vals = mapper.run(src_vals)
    assert_array_almost_equal(dst_vals, np.array([0.0, 1.0, 0.0, 3.0, 4.0, 5.0]))


def test_bad_destination():
    src = Rectilinear([0, 1, 2], [0, 2])
    dst = Rectilinear([0.5, 1.5, 2.5], [0.25, 1.25])

    mapper = NearestVal()
    mapper.initialize(dst, src)

    src_vals = np.arange(src.get_point_count())
    dst_vals = [0.0] * src.get_point_count()
    with pytest.raises(TypeError):
        mapper.run(src_vals, dst_vals)


def test_find_mapper():
    src = Rectilinear([0, 1, 2], [0, 2])
    dst = Rectilinear([0.5, 1.5, 2.5], [0.25, 1.25])

    mappers = find_mapper(dst, src)

    assert len(mappers) == 3
    assert mappers[0].name == "PointToPoint"
    assert isinstance(mappers[0], NearestVal)


def test_incompatible_grids():
    grid = Rectilinear([0, 1, 2], [0, 2])

    mapper = NearestVal()

    assert not mapper.test(grid, None)
    assert not mapper.test(None, grid)
    assert mapper.test(grid, grid)
