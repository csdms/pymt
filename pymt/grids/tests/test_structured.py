import unittest

import numpy as np

from pymt.grids import Structured, StructuredPoints
from .test_utils import NumpyArrayMixIn


class TestStructuredGrid(unittest.TestCase, NumpyArrayMixIn):
    def test_1d(self):
        grid = Structured([-1, 2, 3, 6], (4, ))
        self.assertEqual(grid.get_point_count(), 4)
        self.assertEqual(grid.get_cell_count(), 3)
        self.assertArrayEqual(grid.get_x(), np.array([-1., 2., 3., 6.]))
        with self.assertRaises(IndexError):
            grid.get_y()
        self.assertArrayEqual(grid.get_shape(), (4, ))
        self.assertArrayEqual(grid.get_offset(), np.array([2, 4, 6]))
        self.assertArrayEqual(grid.get_connectivity(),
                              np.array([0, 1, 1, 2, 2, 3]))

    def test_2d_points(self):
        (x, y) = np.meshgrid([1., 2., 4., 8.], [1., 2., 3.])
        grid = StructuredPoints(y.flatten(), x.flatten(), (3, 4),
                                set_connectivity=True)
        self.assertEqual(grid.get_point_count(), 12)
        self.assertEqual(grid.get_cell_count(), 0)

        self.assertArrayEqual(
            grid.get_x(),
            np.array([1., 2., 4., 8., 1., 2., 4., 8., 1., 2., 4., 8.]))
        self.assertArrayEqual(
            grid.get_y(),
            np.array([1., 1., 1., 1., 2., 2., 2., 2., 3., 3., 3., 3.]))
        self.assertArrayEqual(grid.get_shape(), (3, 4))

        self.assertArrayEqual(
            grid.get_offset(),
            np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))
        self.assertArrayEqual(
            grid.get_connectivity(),
            np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]))

    def test_2d(self):
        (x, y) = np.meshgrid([1., 2., 4., 8.], [1., 2., 3.])
        grid = Structured(y.flatten(), x.flatten(), [3, 4])
        self.assertEqual(grid.get_point_count(), 12)
        self.assertEqual(grid.get_cell_count(), 6)
        self.assertArrayEqual(
            grid.get_x(),
            np.array([1., 2., 4., 8., 1., 2., 4., 8., 1., 2., 4., 8.]))
        self.assertArrayEqual(
            grid.get_y(),
            np.array([1., 1., 1., 1., 2., 2., 2., 2., 3., 3., 3., 3.]))
        self.assertArrayEqual(grid.get_shape(), [3, 4])
        self.assertArrayEqual(
            grid.get_offset(), np.array([4, 8, 12, 16, 20, 24]))
        self.assertArrayEqual(
            grid.get_connectivity(),
            np.array([0, 1,  5, 4,
                      1, 2,  6, 5,
                      2, 3,  7, 6,
                      4, 5,  9, 8,
                      5, 6, 10, 9,
                      6, 7, 11, 10]))

    def test_3d(self):
        x = [0, 1, 0, 1, 0, 1, 0, 1]
        y = [0, 0, 1, 1, 0, 0, 1, 1]
        z = [0, 0, 0, 0, 1, 1, 1, 1]

        grid = Structured(z, y, x, (2, 2, 2))

        self.assertArrayEqual(grid.get_x(),
                              np.array([0., 1., 0., 1., 0., 1., 0., 1.]))
        self.assertArrayEqual(grid.get_y(),
                              np.array([0., 0., 1., 1., 0., 0., 1., 1.]))
        self.assertArrayEqual(grid.get_z(),
                              np.array([0., 0., 0., 0., 1., 1., 1., 1.]))
        self.assertArrayEqual(grid.get_offset(), np.array([8]))
        self.assertArrayEqual(grid.get_connectivity(),
                              np.array([0, 1, 3, 2, 4, 5, 7, 6]))

        grid = Structured(x, y, z, (2, 2, 2), ordering='ccw')
        self.assertArrayEqual(grid.get_connectivity(),
                              np.array([1, 0, 2, 3, 5, 4, 6, 7]))

    def test_get_axis_coordinates(self):
        grid = Structured((1, 1, 4, 4, 5, 5), (2, 3, 2, 3, 2, 3), (3, 2),
                          units=('m', 'km'))

        self.assertArrayEqual(grid.get_axis_coordinates(0),
                              np.array([1., 1., 4., 4., 5., 5.]))
        self.assertArrayEqual(grid.get_axis_coordinates(1),
                              np.array([2., 3., 2., 3., 2., 3.]))
