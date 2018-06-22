import unittest
import sys

import numpy as np
import six

from pymt.grids import Unstructured
from .test_utils import NumpyArrayMixIn


class TestUnstructuredGrid(unittest.TestCase, NumpyArrayMixIn):
    def test_1d_points(self):
        grid = Unstructured([0., 6., 9., 11.],
                            connectivity=[0, 1, 2, 3], offset=[1, 2, 3, 4])
        self.assertEqual(grid.get_point_count(), 4)
        self.assertEqual(grid.get_cell_count(), 4)
        self.assertEqual(grid.get_dim_count(), 1)

        self.assertArrayEqual(grid.get_x(), np.array([0., 6., 9., 11.]))
        with self.assertRaises(IndexError):
            self.assertArrayEqual(grid.get_y(), np.array([0., 0., 1., 1.]))
        self.assertArrayEqual(grid.get_connectivity(),
                              np.array([0, 1, 2, 3]))
        self.assertArrayEqual(grid.get_offset(), np.array([1, 2, 3, 4]))

    def test_2d_tri_cells(self):
        grid = Unstructured([0, 0, 1, 1], [0, 2, 1, 3],
                            connectivity=[0, 2, 1, 2, 3, 1], offset=[3, 6])
        self.assertEqual(grid.get_point_count(), 4)
        self.assertEqual(grid.get_cell_count(), 2)
        self.assertEqual(grid.get_dim_count(), 2)

        self.assertArrayEqual(grid.get_x(), np.array([0., 2., 1., 3.]))
        self.assertArrayEqual(grid.get_y(), np.array([0., 0., 1., 1.]))
        self.assertArrayEqual(grid.get_connectivity(),
                              np.array([0, 2, 1, 2, 3, 1]))
        self.assertArrayEqual(grid.get_offset(), np.array([3, 6]))

    def test_3d_cube_cells(self):
        x = [0, 1, 0, 1, 0, 1, 0, 1]
        y = [0, 0, 1, 1, 0, 0, 1, 1]
        z = [0, 0, 0, 0, 1, 1, 1, 1]
        grid = Unstructured(z, y, x, connectivity=[0, 1, 2, 3, 4, 5, 6, 7],
                            offset=[8])
        self.assertEqual(grid.get_point_count(), 8)
        self.assertEqual(grid.get_cell_count(), 1)
        self.assertArrayEqual(grid.get_x(),
                              np.array([0., 1., 0., 1., 0., 1., 0., 1.]))
        self.assertArrayEqual(grid.get_y(),
                              np.array([0., 0., 1., 1., 0., 0., 1., 1.]))
        self.assertArrayEqual(grid.get_z(),
                              np.array([0., 0., 0., 0., 1., 1., 1., 1.]))
        self.assertArrayEqual(grid.get_connectivity(),
                              np.array([0, 1, 2, 3, 4, 5, 6, 7]))
        self.assertArrayEqual(grid.get_offset(), np.array([8]))

    def test_connectivity_as_matrix_same_shape(self):
        grid = Unstructured([0, 0, 1, 1], [0, 2, 1, 3],
                            connectivity=[0, 2, 1, 2, 3, 1], offset=[3, 6])
        self.assertArrayEqual(grid.get_connectivity(),
                              np.array([0, 2, 1, 2, 3, 1]))
        mat, fill_val = grid.get_connectivity_as_matrix()
        self.assertArrayEqual(mat, np.array([[0, 2, 1], [2, 3, 1]]))
        self.assertEqual(fill_val, six.MAXSIZE)

    def test_connectivity_as_matrix_mixed_shapes(self):
        grid = Unstructured([0, 1, 2, 1, 2], [0, 0, 0, 1, 1],
                            connectivity=[0, 1, 3, 1, 2, 4, 3], offset=[3, 7])
        mat, fill_val = grid.get_connectivity_as_matrix(fill_val=-1)
        self.assertArrayEqual(mat, np.array([[0, 1, 3, -1], [1, 2, 4, 3]]))
        self.assertEqual(fill_val, -1)

        grid = Unstructured([0, 1, 2, 1, 2], [0, 0, 0, 1, 1],
                            connectivity=[3, 1, 2, 4, 0, 3, 1], offset=[4, 7])
        mat, fill_val = grid.get_connectivity_as_matrix(fill_val=999)
        self.assertArrayEqual(mat, np.array([[3, 1, 2, 4], [0, 3, 1, 999]]))
        self.assertEqual(fill_val, 999)
