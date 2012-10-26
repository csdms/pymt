#! /usr/bin/env python

import unittest
from cmt.grids import UniformRectilinear, UniformRectilinearPoints
import numpy as np

class BaseRasterTest (object):
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

    def test_spacing (self):
        spacing = self.grid.get_spacing ()
        self.assertEqual (len (spacing), len (spacing))
        self.assertListEqual (list (self.spacing), list (spacing))

    def test_origin (self):
        origin = self.grid.get_origin ()
        self.assertEqual (len (origin), len (self.origin))
        self.assertListEqual (list (self.origin), list (origin))

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

class TestGridsUniformRectilinearXYIndexing (BaseRasterTest, unittest.TestCase):
    point_count = 6
    cell_count = 2
    shape = (3, 2)
    spacing = (2., 1.)
    origin = (0., .5)
    x = [0.5, 1.5, 0.5, 1.5, 0.5, 1.5]
    y = [0., 0., 2., 2., 4., 4.]
    x_units = '-'
    y_units = '-'
    z_units = '-'

    def setUp (self):
        self.grid = UniformRectilinear ((2,3), (1,2), (.5, 0))

class TestGridsUniformRectilinearIJIndexing (BaseRasterTest, unittest.TestCase):
    point_count = 6
    cell_count = 2
    shape = (2, 3)
    spacing = (1., 2.)
    origin = (.5, .0)
    x = [0., 2., 4., 0., 2., 4.]
    y = [0.5, 0.5, 0.5, 1.5, 1.5, 1.5]
    x_units = 'km'
    y_units = 'm'
    z_units = '-'

    def setUp (self):
        self.grid = UniformRectilinear ((2,3), (1,2), (.5, 0), indexing='ij', units=('m', 'km'))

class TestGridsUniformRectilinearPoints (BaseRasterTest, unittest.TestCase):
    point_count = 6
    cell_count = 0
    shape = (2, 3)
    spacing = (1., 2.)
    origin = (.5, 0.)
    x = [0., 2., 4., 0., 2., 4.]
    y = [0.5, 0.5, 0.5, 1.5, 1.5, 1.5]
    x_units = '-'
    y_units = '-'
    z_units = '-'

    def setUp (self):
        self.grid = UniformRectilinearPoints ((2,3), (1,2), (.5, 0), indexing='ij', set_connectivity=True)

    def test_connectivity (self):
        c = self.grid.get_connectivity ()
        self.assertTrue (np.all (c == np.arange (self.point_count)))

    def test_offset (self):
        o = self.grid.get_offset ()
        self.assertTrue (np.all (o == np.arange (1, self.point_count+1)))

class TestGridsUniformRectilinear1D (BaseRasterTest, unittest.TestCase):
    point_count = 5
    cell_count = 0
    shape = (5, )
    spacing = (1., )
    origin = (.5, )
    x = [0.5, 1.5, 2.5, 3.5, 4.5]
    y = [0., 0., 0., 0., 0.]
    x_units = '-'
    y_units = '-'
    z_units = '-'

    def setUp (self):
        self.grid = UniformRectilinearPoints ((5, ), (1., ), (.5,), indexing='ij', set_connectivity=True)

    def test_connectivity (self):
        c = self.grid.get_connectivity ()
        self.assertTrue (np.all (c == np.arange (self.point_count)))

    def test_offset (self):
        o = self.grid.get_offset ()
        self.assertTrue (np.all (o == np.arange (1, self.point_count+1)))

class TestGridsUniformRectilinearXYIndexing3D (BaseRasterTest, unittest.TestCase):
    point_count = 24
    cell_count = 6
    shape = (2, 3, 4)
    spacing = (3., 2., 1.)
    origin = (1., 0., -1.)
    x = [-1., 0., 1., 2., -1., 0., 1., 2., -1., 0., 1., 2., -1., 0., 1., 2., -1., 0., 1., 2., -1., 0., 1., 2.]
    y = [ 0., 0., 0., 0., 2., 2., 2., 2., 4., 4., 4., 4., 0., 0., 0., 0., 2., 2., 2., 2., 4., 4., 4., 4.]
    z = [ 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4.]
    x_units = '-'
    y_units = '-'
    z_units = '-'

    def setUp (self):
        self.grid = UniformRectilinear ((4, 3, 2), (1, 2, 3), (-1, 0, 1), indexing='xy')

    def test_z (self):
        self.assertListEqual (self.z, list (self.grid.get_z ()))

    def test_offset (self):
        o = self.grid.get_offset ()
        self.assertTrue (np.all (o == 8. * np.arange (1, self.cell_count+1)))

class TestGridsUniformRectilinearIJIndexing3D (BaseRasterTest, unittest.TestCase):
    point_count = 24
    cell_count = 6
    shape = (4, 3, 2)
    spacing = (1., 2., 3)
    origin = (-1., 0., 1.)
    x_units = '-'
    y_units = '-'
    z_units = '-'
    x = [ 1., 4., 1., 4., 1., 4., 1., 4., 1., 4., 1., 4., 1., 4., 1., 4., 1., 4., 1., 4., 1., 4., 1., 4.]
    y = [ 0., 0., 2., 2., 4., 4., 0., 0., 2., 2., 4., 4., 0., 0., 2., 2., 4., 4., 0., 0., 2., 2., 4., 4.]
    z = [-1., -1., -1., -1., -1., -1., 0., 0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1., 2., 2., 2., 2., 2., 2.]

    def setUp (self):
        self.grid = UniformRectilinear ((4, 3, 2), (1, 2, 3), (-1, 0, 1), indexing='ij')

    def test_z (self):
        self.assertListEqual (self.z, list (self.grid.get_z ()))

    def test_offset (self):
        o = self.grid.get_offset ()
        self.assertTrue (np.all (o == 8. * np.arange (1, self.cell_count+1)))

if __name__ == '__main__':
    unittest.main ()

