#! /usr/bin/env python

import numpy as np
from numpy.testing import assert_array_equal

from pymt.grids.map import UniformRectilinearMap as UniformRectilinear
from pymt.grids.map import UnstructuredPointsMap as UnstructuredPoints
from pymt.mappers import CellToPoint, PointToCell


def test_cell_to_point():
    # The source grid looks like,
    #
    #    (0) ------ (1)
    #     |          |
    #     |          |
    #    (2) ------ (3)
    #     |          |
    #     |          |
    #    (4) ------ (5)
    #     |          |
    #     |          |
    #    (7) ------ (7)
    #

    (dst_x, dst_y) = (np.array([0.45, 1.25, 3.5]), np.array([0.75, 2.25, 3.25]))

    src = UniformRectilinear((2, 4), (2, 1), (0, 0))
    dst = UnstructuredPoints(dst_x, dst_y)

    src_vals = np.arange(src.get_cell_count(), dtype=np.float)

    mapper = CellToPoint()
    mapper.initialize(dst, src)
    dst_vals = mapper.run(src_vals, bad_val=-999)

    assert_array_equal(dst_vals, [0.0, 2.0, -999.0])

    src_vals = np.arange(src.get_cell_count(), dtype=np.float)
    src_vals[0] = -9999
    dst_vals = np.zeros(dst.get_point_count()) + 100
    mapper.run(src_vals, dst_vals=dst_vals)

    assert_array_equal(dst_vals, [100.0, 2.0, -999.0])


def test_point_to_cell():
    (src_x, src_y) = (
        np.array([0.45, 1.25, 3.5, 0.0, 1.0]),
        np.array([0.75, 2.25, 3.25, 0.9, 1.1]),
    )

    src = UnstructuredPoints(src_x, src_y)
    dst = UniformRectilinear((2, 4), (2, 1), (0, 0))

    src_vals = np.arange(src.get_point_count(), dtype=np.float)

    mapper = PointToCell()
    mapper.initialize(dst, src)

    dst_vals = mapper.run(src_vals, bad_val=-999)
    assert_array_equal(dst_vals, [1.5, 4.0, 1.0])

    dst_vals = mapper.run(src_vals, bad_val=-999, method=np.sum)
    assert_array_equal(dst_vals, [3.0, 4.0, 1.0])

    src_vals[0] = -9999
    dst_vals = np.zeros(dst.get_cell_count()) - 1
    mapper.run(src_vals, dst_vals=dst_vals)
    assert_array_equal(dst_vals, [-1.0, 4.0, 1.0])


def test_point_to_cell_on_edges():
    (src_x, src_y) = (
        np.array([0, 0.5, 1.0, 2, 3.5]),
        np.array([1.0, 1.0, 0.0, 3, 3.0]),
    )
    src = UnstructuredPoints(src_x, src_y)
    dst = UniformRectilinear((2, 4), (2, 1), (0, 0))

    mapper = PointToCell()
    mapper.initialize(dst, src)

    src_vals = np.arange(src.get_point_count(), dtype=np.float)
    dst_vals = np.zeros(dst.get_cell_count()) - 1
    mapper.run(src_vals, dst_vals=dst_vals)
    assert_array_equal(dst_vals, [1.0, 0.5, 3.0])


def test_point_to_cell_big():
    (m, n) = (20, 40)
    (src_x, src_y) = np.meshgrid(range(m), range(n))
    src = UnstructuredPoints(src_y, src_x)
    dst = UniformRectilinear((n + 1, m + 1), (1, 1), (-0.5, -0.5))

    mapper = PointToCell()
    mapper.initialize(dst, src)

    src_vals = np.arange(src.get_point_count(), dtype=np.float)
    dst_vals = np.zeros(dst.get_cell_count(), dtype=np.float) - 1
    mapper.run(src_vals, dst_vals=dst_vals)
    assert_array_equal(dst_vals, src_vals)
