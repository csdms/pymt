#! /usr/bin/env python

import unittest
from cmt.grids import UniformRectilinear
import numpy as np

class TestGridsUniformRectilinear (unittest.TestCase):
    def setUp (self):
        self.grid = UniformRectilinear ((2,3), (1,2), (.5, 0))

    def test_point_count (self):
        self.assertEqual (6, self.grid.get_point_count ())

    def test_cell_count (self):
        self.assertEqual (2, self.grid.get_cell_count ())

    def test_x (self):
        self.assertTrue (np.all ([0.5, 1.5, 0.5, 1.5, 0.5, 1.5] == self.grid.get_x ()))

    def test_y (self):
        self.assertTrue (np.all ([0., 0., 2., 2., 4., 4.] == self.grid.get_y ()))

    def test_spacing (self):
        spacing = self.grid.get_spacing ()
        self.assertEqual (len (spacing), 2)
        self.assertTrue (spacing[0] == 2. and spacing[1] == 1.)
    def test_origin (self):
        origin = self.grid.get_origin ()
        self.assertEqual (len (origin), 2)
        self.assertTrue (origin[0] == 0. and origin[1] == .5)

    def test_units (self):
        self.assertEqual ('-', self.grid.get_x_units ())
        self.assertEqual ('-', self.grid.get_y_units ())

if __name__ == '__main__':
    unittest.main ()

