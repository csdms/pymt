import unittest
import numpy as np
from numpy.testing import assert_array_equal

import cmt.grids.utils as utils


class NumpyArrayMixIn(object):
    def assertArrayEqual(self, actual, expected):
        try:
            assert_array_equal(actual, expected)
        except AssertionError as error:
            self.fail(error)


class TestCoordinateUnits(unittest.TestCase):
    def test_one_dim(self):
        self.assertListEqual(['-'], utils.get_default_coordinate_units(1))

    def test_two_dim(self):
        self.assertListEqual(['-', '-'], utils.get_default_coordinate_units(2))

    def test_three_dim(self):
        self.assertListEqual(['-', '-', '-'],
                             utils.get_default_coordinate_units(3))

    def test_zero_dim(self):
        with self.assertRaises(ValueError):
            utils.get_default_coordinate_units(0)

    def test_four_dim(self):
        with self.assertRaises(ValueError):
            utils.get_default_coordinate_units(4)


class TestCoordinateNames(unittest.TestCase):
    def test_one_dim(self):
        self.assertListEqual(['x'], utils.get_default_coordinate_names(1))

    def test_two_dim(self):
        self.assertListEqual(['y', 'x'], utils.get_default_coordinate_names(2))

    def test_three_dim(self):
        self.assertListEqual(['z', 'y', 'x'],
                             utils.get_default_coordinate_names(3))

    def test_zero_dim(self):
        with self.assertRaises(ValueError):
            utils.get_default_coordinate_units(0)

    def test_four_dim(self):
        with self.assertRaises(ValueError):
            utils.get_default_coordinate_units(4)


class TestArraysAreEqualSize(unittest.TestCase):
    def test_one_array(self):
        utils.assert_arrays_are_equal_size(np.empty(5.))

    def test_two_arrays_equal_size(self):
        utils.assert_arrays_are_equal_size(np.empty(5.), np.empty(5))

    def test_two_arrays_unequal_size(self):
        with self.assertRaises(AssertionError):
            utils.assert_arrays_are_equal_size(np.empty(5.), np.empty(4))


class TestArgsAsNumpyArrays(unittest.TestCase, NumpyArrayMixIn):
    def test_one_numpy_arg(self):
        in_arr = np.array([2, 3, 4, 5])
        out_arr = utils.args_as_numpy_arrays(in_arr)
        self.assertIsInstance(out_arr, tuple)
        self.assertTrue(len(out_arr), 1)
        self.assertArrayEqual(out_arr[0], in_arr)

    def test_two_numpy_arg(self):
        in_args = (np.array([2, 3, 4, 5]), np.array([1, 2]))
        out_args = utils.args_as_numpy_arrays(*in_args)

        self.assertIsInstance(out_args, tuple)
        self.assertTrue(len(out_args), len(in_args))
        for (in_arg, out_arg) in zip(in_args, out_args):
            self.assertArrayEqual(out_arg, in_arg)

    def test_list_arg(self):
        in_args = ([2, 3, 4, 5], )
        out_args = utils.args_as_numpy_arrays(*in_args)

        self.assertIsInstance(out_args, tuple)
        self.assertTrue(len(out_args), len(in_args))
        for (in_arg, out_arg) in zip(in_args, out_args):
            self.assertArrayEqual(out_arg, np.array(in_arg))

    def test_tuple_arg(self):
        in_args = ((2, 3, 4, 5), )
        out_args = utils.args_as_numpy_arrays(*in_args)

        self.assertIsInstance(out_args, tuple)
        self.assertTrue(len(out_args), len(in_args))
        for (in_arg, out_arg) in zip(in_args, out_args):
            self.assertArrayEqual(out_arg, np.array(in_arg))


class TestCoordinatesAsNumpyMatrix(unittest.TestCase, NumpyArrayMixIn):
    def test_one_numpy_array(self):
        matrix = utils.coordinates_to_numpy_matrix(np.array([0., 1., 2.]))
        self.assertArrayEqual(matrix, np.array([[0., 1., 2.]]))

    def test_arrays_are_always_float(self):
        matrix = utils.coordinates_to_numpy_matrix(np.array([0, 1, 2]))
        self.assertArrayEqual(matrix, np.array([[0., 1., 2.]]))

    def test_one_list(self):
        matrix = utils.coordinates_to_numpy_matrix([0, 1, 2])
        self.assertArrayEqual(matrix, np.array([[0., 1., 2.]]))

    def test_one_tuple(self):
        matrix = utils.coordinates_to_numpy_matrix((0, 1, 2))
        self.assertArrayEqual(matrix, np.array([[0., 1., 2.]]))

    def test_three_arrays(self):
        matrix = utils.coordinates_to_numpy_matrix(np.array([0, 1, 2]),
                                                   np.array([3, 4, 5]),
                                                   np.array([6, 7, 8]))
        self.assertArrayEqual(matrix, np.array([[0., 1., 2.],
                                                [3., 4., 5.],
                                                [6., 7., 8.]]))

    def test_ndarrays(self):
        matrix = utils.coordinates_to_numpy_matrix(
            np.array([[0, 1, 2], [3, 4, 5]]))
        self.assertArrayEqual(matrix, np.array([[0., 1., 2., 3., 4., 5.]]))
