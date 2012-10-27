#! /usr/bin/env python

import unittest
from cmt.grids import UniformRectilinear, UniformRectilinearPoints
import numpy as np

class TestRasterGrid (unittest.TestCase):

    def assert_point_count (self, grid, point_count):
        self.assertEqual (point_count, grid.get_point_count ())
    def assert_cell_count (self, grid, cell_count):
        self.assertEqual (cell_count, grid.get_cell_count ())

    def assert_shape (self, grid, shape):
        self.assertListEqual (list (grid.get_shape ()), list (shape))
    def assert_spacing (self, grid, spacing):
        self.assertListEqual (list (grid.get_spacing ()), list (spacing))
    def assert_origin (self, grid, origin):
        self.assertListEqual (list (grid.get_origin ()), list (origin))

    def assert_x (self, grid, x):
        self.assertListEqual (list (x), list (grid.get_x ()))
    def assert_y (self, grid, y):
        self.assertListEqual (list (y), list (grid.get_y ()))
    def assert_z (self, grid, z):
        self.assertListEqual (list (z), list (grid.get_z ()))

    def assert_offset (self, grid, offset):
        self.assertListEqual (list (offset), list (grid.get_offset ()))
    def assert_connectivity (self, grid, connectivity):
        self.assertListEqual (list (connectivity), list (grid.get_connectivity ()))

    def test_xy_indexing (self):
        grid = UniformRectilinear ((2,3), (1,2), (.5, 0))
        self.assert_point_count (grid, 6)
        self.assert_cell_count (grid, 2)
        self.assert_shape (grid, (3, 2))
        self.assert_spacing (grid, (2., 1.))
        self.assert_origin (grid, (0., .5))
        self.assert_x (grid, [0.5, 1.5, 0.5, 1.5, 0.5, 1.5])
        self.assert_y (grid, [0., 0., 2., 2., 4., 4.])

    def test_ij_indexing (self):
        grid = UniformRectilinear ((2,3), (1,2), (.5, 0),
                                   indexing='ij', units=('m', 'km'))
        self.assert_point_count (grid, 6)
        self.assert_cell_count (grid, 2)
        self.assert_shape (grid, (2, 3))
        self.assert_spacing (grid, (1., 2.))
        self.assert_origin (grid, (0.5, .0))
        self.assert_x (grid, [0., 2., 4., 0., 2., 4.])
        self.assert_y (grid, [0.5, 0.5, 0.5, 1.5, 1.5, 1.5])

    def test_grid_of_points (self):
        grid = UniformRectilinearPoints (
            (2,3), (1,2), (.5, 0), indexing='ij', set_connectivity=True)
        self.assert_point_count (grid, 6)
        self.assert_cell_count (grid, 0)
        self.assert_shape (grid, (2, 3))
        self.assert_spacing (grid, (1., 2.))
        self.assert_origin (grid, (0.5, .0))
        self.assert_x (grid, [0., 2., 4., 0., 2., 4.])
        self.assert_y (grid, [0.5, 0.5, 0.5, 1.5, 1.5, 1.5])
        self.assert_connectivity (grid, np.arange (grid.get_point_count ()))
        self.assert_offset (grid, np.arange (1, grid.get_point_count ()+1))

    def test_1d_grid_of_points (self):
        grid = UniformRectilinearPoints (
            (5, ), (1., ), (.5,), indexing='ij', set_connectivity=True)
        self.assert_point_count (grid, 5)
        self.assert_cell_count (grid, 0)
        self.assert_shape (grid, (5, ))
        self.assert_spacing (grid, (1., ))
        self.assert_origin (grid, (0.5, ))
        self.assert_x (grid, [0.5, 1.5, 2.5, 3.5, 4.5])
        self.assert_y (grid, [0., 0., 0., 0., 0.])
        self.assert_connectivity (grid, np.arange (grid.get_point_count ()))
        self.assert_offset (grid, np.arange (1, grid.get_point_count ()+1))

    def test_3d_grid_xy_indexing (self):
        grid = UniformRectilinear ((4, 3, 2), (1, 2, 3), (-1, 0, 1),
                                   indexing='xy')
        self.assert_point_count (grid, 24)
        self.assert_cell_count (grid, 6)
        self.assert_shape (grid, (2, 3, 4))
        self.assert_spacing (grid, (3., 2., 1.))
        self.assert_origin (grid, (1., 0., -1.))
        self.assert_x (grid, [-1., 0., 1., 2., -1., 0., 1., 2.,
                              -1., 0., 1., 2., -1., 0., 1., 2.,
                              -1., 0., 1., 2., -1., 0., 1., 2.])
        self.assert_y (grid, [0., 0., 0., 0., 2., 2., 2., 2.,
                              4., 4., 4., 4., 0., 0., 0., 0.,
                              2., 2., 2., 2., 4., 4., 4., 4.])
        self.assert_z (grid, [1., 1., 1., 1., 1., 1.,
                              1., 1., 1., 1., 1., 1.,
                              4., 4., 4., 4., 4., 4.,
                              4., 4., 4., 4., 4., 4.])
        self.assert_offset (grid, 8. * np.arange (1, grid.get_cell_count ()+1))

    def test_3d_grid_ij_indexing (self):
        grid = UniformRectilinear ((4, 3, 2), (1, 2, 3), (-1, 0, 1),
                                   indexing='ij')

        self.assert_point_count (grid, 24)
        self.assert_cell_count (grid, 6)
        self.assert_shape (grid, (4, 3, 2))
        self.assert_spacing (grid, (1., 2., 3.))
        self.assert_origin (grid, (-1., 0., 1.))
        self.assert_x (grid, [1., 4., 1., 4., 1., 4., 1., 4.,
                              1., 4., 1., 4., 1., 4., 1., 4.,
                              1., 4., 1., 4., 1., 4., 1., 4.])
        self.assert_y (grid, [0., 0., 2., 2., 4., 4., 0., 0.,
                              2., 2., 4., 4., 0., 0., 2., 2.,
                              4., 4., 0., 0., 2., 2., 4., 4.])
        self.assert_z (grid, [-1., -1., -1., -1., -1., -1.,
                              0., 0., 0., 0., 0., 0.,
                              1., 1., 1., 1., 1., 1.,
                              2., 2., 2., 2., 2., 2.])
        self.assert_offset (grid, 8. * np.arange (1, grid.get_cell_count ()+1))

def suite ():
    suite = unittest.TestLoader ().loadTestsFromTestCase (TestRasterGrid)
    return suite

if __name__ == '__main__':
    unittest.main ()

