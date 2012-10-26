#! /usr/bin/env python

import unittest
from cmt.grids import Rectilinear, RectilinearPoints
import numpy as np

class BaseRectilinearTest (object):
    def test_point_count (self):
        self.assertEqual (self.point_count, self.grid.get_point_count ())

    def test_cell_count (self):
        self.assertEqual (self.cell_count, self.grid.get_cell_count ())

    def test_x (self):
        self.assertListEqual (self.x, list (self.grid.get_x ()))

    def test_y (self):
        self.assertListEqual (self.y, list (self.grid.get_y ()))

    def test_shape (self):
        shape = self.grid.get_shape ()
        self.assertEqual (len (shape), len (self.shape))
        self.assertListEqual (list (self.shape), list (shape))

    def test_units (self):
        self.assertEqual (self.x_units, self.grid.get_x_units ())
        self.assertEqual (self.y_units, self.grid.get_y_units ())

        self.assertEqual (self.x_units, self.grid.get_x_units ())
        self.assertEqual (self.y_units, self.grid.get_y_units ())
        self.assertEqual (self.z_units, self.grid.get_z_units ())

        self.assertEqual (self.y_units, self.grid.get_coordinate_units (0))
        self.assertEqual (self.x_units, self.grid.get_coordinate_units (1))
        self.assertEqual (self.z_units, self.grid.get_coordinate_units (2))

    def test_offset (self):
        o = self.grid.get_offset ()
        self.assertListEqual (range (4, (self.cell_count+1)*4, 4), list (o))

class TestGridsRectilinearXYIndexing (BaseRectilinearTest, unittest.TestCase):
    point_count = 12
    cell_count = 6
    shape = (3, 4)
    x = [ 1., 2., 4., 8., 1., 2., 4., 8., 1., 2., 4., 8.]
    y = [ 1., 1., 1., 1., 2., 2., 2., 2., 3., 3., 3., 3.]
    x_units = '-'
    y_units = '-'
    z_units = '-'

    def setUp (self):
        self.grid = Rectilinear ([1., 2., 4., 8.], [1., 2., 3.])

class TestGridsRectilinearIJIndexing (BaseRectilinearTest, unittest.TestCase):
    point_count = 12
    cell_count = 6
    shape = (4, 3)
    x = [ 1., 2., 3., 1., 2., 3., 1., 2., 3., 1., 2., 3.]
    y = [ 1., 1., 1., 2., 2., 2., 4., 4., 4., 8., 8., 8.]
    x_units = '-'
    y_units = '-'
    z_units = '-'

    def setUp (self):
        self.grid = Rectilinear ([1., 2., 4., 8.], [1., 2., 3.], indexing='ij')

    def test_connectivity (self):
        c = self.grid.get_connectivity ()
        self.assertListEqual ([0, 1, 4, 3, 1, 2, 5, 4, 3, 4, 7, 6, 4, 5, 8, 7, 6, 7, 10, 9, 7, 8, 11, 10],
                              list (c))

class TestGridsRectilinearPoints (BaseRectilinearTest, unittest.TestCase):
    point_count = 12
    cell_count = 0
    shape = (4, 3)
    x = [ 1., 2., 3., 1., 2., 3., 1., 2., 3., 1., 2., 3.]
    y = [ 1., 1., 1., 2., 2., 2., 4., 4., 4., 8., 8., 8.]
    x_units = '-'
    y_units = '-'
    z_units = '-'

    def setUp (self):
        self.grid = RectilinearPoints ([1., 2., 4., 8.], [1., 2., 3.], indexing='ij', set_connectivity=True)

    def test_connectivity (self):
        c = self.grid.get_connectivity ()
        self.assertTrue (np.all (c == np.arange (self.point_count)))

    def test_offset (self):
        o = self.grid.get_offset ()
        self.assertTrue (np.all (o == np.arange (1, self.point_count+1)))

class TestGridsRectilinear1D (BaseRectilinearTest, unittest.TestCase):
    point_count = 5
    cell_count = 4
    shape = (5, )
    x = [ 1., 3., 4., 5., 6.]
    y = [0., 0., 0., 0., 0.]
    x_units = '-'
    y_units = '-'
    z_units = '-'

    def setUp (self):
        self.grid = Rectilinear ([1,3,4,5,6], set_connectivity=True)

    def test_connectivity (self):
        c = self.grid.get_connectivity ()
        self.assertListEqual ([0, 1, 1, 2, 2, 3, 3, 4], list (c))

    def test_offset (self):
        o = self.grid.get_offset ()
        self.assertListEqual ([2, 4, 6, 8], list (o))

class TestGridsRectilinearXYIndexing3D (BaseRectilinearTest, unittest.TestCase):
    point_count = 24
    cell_count = 6
    shape = (2, 3, 4)
    x = [ 0., 1., 2., 3., 0., 1., 2., 3., 0., 1., 2., 3., 0., 1., 2., 3., 0., 1., 2., 3., 0., 1., 2., 3.]
    y = [ 4., 4., 4., 4., 5., 5., 5., 5., 6., 6., 6., 6., 4., 4., 4., 4., 5., 5., 5., 5., 6., 6., 6., 6.]
    z = [ 7., 7., 7., 7., 7., 7., 7., 7., 7., 7., 7., 7., 8., 8., 8., 8., 8., 8., 8., 8., 8., 8., 8., 8.]
    x_units = '-'
    y_units = '-'
    z_units = '-'


    def setUp (self):
        self.grid = Rectilinear ([0, 1, 2, 3], [4, 5, 6], [7, 8], set_connectivity=True, indexing='xy')

    def test_z (self):
        self.assertListEqual (self.z, list (self.grid.get_z ()))

    def test_offset (self):
        o = self.grid.get_offset ()
        self.assertListEqual (list (8. * np.arange (1, self.cell_count+1)), list (o))

class TestGridsRectilinearIJIndexing3D (BaseRectilinearTest, unittest.TestCase):
    point_count = 24
    cell_count = 6
    shape = (4, 3, 2)
    x = [ 7., 8., 7., 8., 7., 8., 7., 8., 7., 8., 7., 8., 7., 8., 7., 8., 7., 8., 7., 8., 7., 8., 7., 8.]
    y = [ 4., 4., 5., 5., 6., 6., 4., 4., 5., 5., 6., 6., 4., 4., 5., 5., 6., 6., 4., 4., 5., 5., 6., 6.]
    z = [ 0., 0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1., 2., 2., 2., 2., 2., 2., 3., 3., 3., 3., 3., 3.]
    x_units = '-'
    y_units = '-'
    z_units = '-'

    def setUp (self):
        self.grid = Rectilinear ([0, 1, 2, 3], [4, 5, 6], [7, 8], set_connectivity=True, indexing='ij')

    def test_z (self):
        self.assertListEqual (self.z, list (self.grid.get_z ()))

    def test_offset (self):
        o = self.grid.get_offset ()
        self.assertListEqual (list (8. * np.arange (1, self.cell_count+1)), list (o))

if __name__ == '__main__':
    unittest.main ()

