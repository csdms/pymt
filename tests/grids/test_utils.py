import unittest

import numpy as np
from numpy.testing import assert_array_equal

import pymt.grids.utils as utils
from pymt.grids import Structured, UniformRectilinear, UnstructuredPoints


class NumpyArrayMixIn:
    def assertArrayEqual(self, actual, expected):
        try:
            assert_array_equal(actual, expected)
        except AssertionError as error:
            self.fail(error)


class TestCoordinateUnits(unittest.TestCase):
    def test_one_dim(self):
        self.assertListEqual(["-"], utils.get_default_coordinate_units(1))

    def test_two_dim(self):
        self.assertListEqual(["-", "-"], utils.get_default_coordinate_units(2))

    def test_three_dim(self):
        self.assertListEqual(["-", "-", "-"], utils.get_default_coordinate_units(3))

    def test_zero_dim(self):
        with self.assertRaises(ValueError):
            utils.get_default_coordinate_units(0)

    def test_four_dim(self):
        with self.assertRaises(ValueError):
            utils.get_default_coordinate_units(4)


class TestCoordinateNames(unittest.TestCase):
    def test_one_dim(self):
        self.assertListEqual(["x"], utils.get_default_coordinate_names(1))

    def test_two_dim(self):
        self.assertListEqual(["y", "x"], utils.get_default_coordinate_names(2))

    def test_three_dim(self):
        self.assertListEqual(["z", "y", "x"], utils.get_default_coordinate_names(3))

    def test_zero_dim(self):
        with self.assertRaises(ValueError):
            utils.get_default_coordinate_units(0)

    def test_four_dim(self):
        with self.assertRaises(ValueError):
            utils.get_default_coordinate_units(4)


class TestArraysAreEqualSize(unittest.TestCase):
    def test_one_array(self):
        utils.assert_arrays_are_equal_size(np.empty(5, dtype=float))

    def test_two_arrays_equal_size(self):
        utils.assert_arrays_are_equal_size(np.empty(5, dtype=float), np.empty(5))

    def test_two_arrays_unequal_size(self):
        with self.assertRaises(AssertionError):
            utils.assert_arrays_are_equal_size(np.empty(5, dtype=float), np.empty(4))


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
        for in_arg, out_arg in zip(in_args, out_args):
            self.assertArrayEqual(out_arg, in_arg)

    def test_list_arg(self):
        in_args = ([2, 3, 4, 5],)
        out_args = utils.args_as_numpy_arrays(*in_args)

        self.assertIsInstance(out_args, tuple)
        self.assertTrue(len(out_args), len(in_args))
        for in_arg, out_arg in zip(in_args, out_args):
            self.assertArrayEqual(out_arg, np.array(in_arg))

    def test_tuple_arg(self):
        in_args = ((2, 3, 4, 5),)
        out_args = utils.args_as_numpy_arrays(*in_args)

        self.assertIsInstance(out_args, tuple)
        self.assertTrue(len(out_args), len(in_args))
        for in_arg, out_arg in zip(in_args, out_args):
            self.assertArrayEqual(out_arg, np.array(in_arg))


class TestCoordinatesAsNumpyMatrix(unittest.TestCase, NumpyArrayMixIn):
    def test_one_numpy_array(self):
        matrix = utils.coordinates_to_numpy_matrix(np.array([0.0, 1.0, 2.0]))
        self.assertArrayEqual(matrix, np.array([[0.0, 1.0, 2.0]]))

    def test_arrays_are_always_float(self):
        matrix = utils.coordinates_to_numpy_matrix(np.array([0, 1, 2]))
        self.assertArrayEqual(matrix, np.array([[0.0, 1.0, 2.0]]))

    def test_one_list(self):
        matrix = utils.coordinates_to_numpy_matrix([0, 1, 2])
        self.assertArrayEqual(matrix, np.array([[0.0, 1.0, 2.0]]))

    def test_one_tuple(self):
        matrix = utils.coordinates_to_numpy_matrix((0, 1, 2))
        self.assertArrayEqual(matrix, np.array([[0.0, 1.0, 2.0]]))

    def test_three_arrays(self):
        matrix = utils.coordinates_to_numpy_matrix(
            np.array([0, 1, 2]), np.array([3, 4, 5]), np.array([6, 7, 8])
        )
        self.assertArrayEqual(
            matrix, np.array([[0.0, 1.0, 2.0], [3.0, 4.0, 5.0], [6.0, 7.0, 8.0]])
        )

    def test_ndarrays(self):
        matrix = utils.coordinates_to_numpy_matrix(np.array([[0, 1, 2], [3, 4, 5]]))
        self.assertArrayEqual(matrix, np.array([[0.0, 1.0, 2.0, 3.0, 4.0, 5.0]]))


class TestsNonSingletonAxes(unittest.TestCase, NumpyArrayMixIn):
    def test_without_singletons(self):
        grid = UniformRectilinear((4, 5), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_axes(grid), np.array((0, 1)))

        grid = UniformRectilinear((5,), (1.0,), (0.0,))
        self.assertArrayEqual(utils.non_singleton_axes(grid), np.array((0,)))

        grid = UniformRectilinear((4, 5, 6), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_axes(grid), np.array((0, 1, 2)))

    def test_with_singletons(self):
        grid = UniformRectilinear((4, 1), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_axes(grid), np.array((0,)))

        grid = UniformRectilinear((1, 4), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_axes(grid), np.array((1,)))

        grid = UniformRectilinear((4, 1, 1), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_axes(grid), np.array((0,)))

        grid = UniformRectilinear((1, 4, 1), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_axes(grid), np.array((1,)))

        grid = UniformRectilinear((1, 4, 5), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_axes(grid), np.array((1, 2)))


class TestsNonSingletonShape(unittest.TestCase, NumpyArrayMixIn):
    def test_without_singletons(self):
        grid = UniformRectilinear((4, 5), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_shape(grid), np.array((4, 5)))

        grid = UniformRectilinear((5,), (1.0,), (0.0,))
        self.assertArrayEqual(utils.non_singleton_shape(grid), np.array((5,)))

        grid = UniformRectilinear((4, 5, 6), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_shape(grid), np.array((4, 5, 6)))

    def test_with_singletons(self):
        grid = UniformRectilinear((4, 1), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_shape(grid), np.array((4,)))

        grid = UniformRectilinear((1, 4), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_shape(grid), np.array((4,)))

        grid = UniformRectilinear((4, 1, 1), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_shape(grid), np.array((4,)))

        grid = UniformRectilinear((1, 4, 1), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_shape(grid), np.array((4,)))

        grid = UniformRectilinear((1, 4, 5), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_shape(grid), np.array((4, 5)))


class TestsNonSingletonCoordinateNames(unittest.TestCase, NumpyArrayMixIn):
    def test_without_singletons(self):
        grid = UniformRectilinear((4, 5), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_coordinate_names(grid), ("y", "x"))

        grid = UniformRectilinear((5,), (1.0,), (0.0,))
        self.assertArrayEqual(utils.non_singleton_coordinate_names(grid), ("x",))

        grid = UniformRectilinear((4, 5, 6), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(
            utils.non_singleton_coordinate_names(grid), ("z", "y", "x")
        )

    def test_with_singletons(self):
        grid = UniformRectilinear((4, 1), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_coordinate_names(grid), ("y",))

        grid = UniformRectilinear((1, 4), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_coordinate_names(grid), ("x",))

        grid = UniformRectilinear((4, 1, 1), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_coordinate_names(grid), ("z",))

        grid = UniformRectilinear((1, 4, 1), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_coordinate_names(grid), ("y",))

        grid = UniformRectilinear((1, 4, 5), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_coordinate_names(grid), ("y", "x"))


class TestsNonSingletonDimensionNames(unittest.TestCase, NumpyArrayMixIn):
    def test_without_singletons(self):
        grid = UniformRectilinear((4, 5), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(
            utils.non_singleton_dimension_names(grid), np.array(["y", "x"])
        )

        grid = UniformRectilinear((5,), (1.0,), (0.0,))
        self.assertArrayEqual(
            utils.non_singleton_dimension_names(grid), np.array(["x"])
        )

        grid = UniformRectilinear((4, 5, 6), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(
            utils.non_singleton_dimension_names(grid), ("z", "y", "x")
        )

    def test_with_singletons(self):
        grid = UniformRectilinear((4, 1), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_dimension_names(grid), ("y",))

        grid = UniformRectilinear((1, 4), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_dimension_names(grid), ("x",))

        grid = UniformRectilinear((4, 1, 1), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_dimension_names(grid), ("z",))

        grid = UniformRectilinear((1, 4, 1), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_dimension_names(grid), ("y",))

        grid = UniformRectilinear((1, 4, 5), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_dimension_names(grid), ("y", "x"))


class TestsNonSingletonDimensionShape(unittest.TestCase, NumpyArrayMixIn):
    def test_without_singletons(self):
        grid = UniformRectilinear((4, 5), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid), np.array([["y"], ["x"]])
        )

        grid = UniformRectilinear((5,), (1.0,), (0.0,))
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid), np.array([["x"]])
        )

        grid = UniformRectilinear((4, 5, 6), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid), np.array([["z"], ["y"], ["x"]])
        )

    def test_with_singletons(self):
        grid = UniformRectilinear((4, 1), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_dimension_shape(grid), (("y",),))

        grid = UniformRectilinear((1, 4), (1.0, 1.0), (0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_dimension_shape(grid), (("x",),))

        grid = UniformRectilinear((4, 1, 1), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_dimension_shape(grid), (("z",),))

        grid = UniformRectilinear((1, 4, 1), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(utils.non_singleton_dimension_shape(grid), (("y",),))

        grid = UniformRectilinear((1, 4, 5), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid), (("y",), ("x",))
        )

    def test_structured_without_singletons(self):
        grid = Structured([0, 0, 0, 1, 1, 1], [1, 2, 3, 1, 2, 3], (2, 3))
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid),
            np.array([["y", "x"], ["y", "x"]]),
        )

        grid = Structured([0, 1, 2, 3, 4], (5,))
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid), np.array([["x"]])
        )

        grid = Structured(
            [0.0] * 6 + [1.0] * 6,
            [0, 0, 0, 1, 1, 1] * 2,
            [1, 2, 3, 1, 2, 3] * 2,
            (2, 3, 2),
        )
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid),
            np.array([["z", "y", "x"], ["z", "y", "x"], ["z", "y", "x"]]),
        )

    def test_structured_with_singletons(self):
        grid = Structured([0, 1, 2, 3], [0] * 4, (4, 1))
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid), np.array([["y"]])
        )

        grid = Structured([0] * 4, [0, 1, 2, 3], (1, 4))
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid), np.array([["x"]])
        )

        grid = Structured([0, 1, 2, 3], [0] * 4, [0] * 4, (4, 1, 1))
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid), np.array([["z"]])
        )

        grid = Structured([0] * 4, [0, 1, 2, 3], [0] * 4, (1, 4, 1))
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid), np.array([["y"]])
        )

        grid = Structured([0] * 6, [0, 0, 1, 1, 2, 2], [0, 1] * 3, (1, 3, 2))
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid),
            np.array([["y", "x"], ["y", "x"]]),
        )

    def test_unstructured_without_singletons(self):
        grid = UnstructuredPoints([0, 0, 0, 1, 1, 1], [1, 2, 3, 1, 2, 3])
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid),
            np.array([["n_node"], ["n_node"]]),
        )

        grid = UnstructuredPoints([0, 1, 2, 3, 4, 5])
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid), np.array([["n_node"]])
        )

        grid = UnstructuredPoints(
            [0.0] * 6 + [1.0] * 6, [0, 0, 0, 1, 1, 1] * 2, [1, 2, 3, 1, 2, 3] * 2
        )
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid),
            np.array([["n_node"], ["n_node"], ["n_node"]]),
        )

    def test_unstructured_with_singletons(self):
        grid = UnstructuredPoints([0, 1, 2, 3], [0] * 4)
        self.assertArrayEqual(
            utils.non_singleton_dimension_shape(grid),
            np.array([["n_node"], ["n_node"]]),
        )


class TestsConnectivityMatrixToArray(unittest.TestCase, NumpyArrayMixIn):
    def test_unequal_node_count(self):
        matrix = np.array([[0, 1, 2, 999], [2, 1, 3, 4]])
        (face_nodes, offset) = utils.connectivity_matrix_as_array(matrix, 999)
        self.assertArrayEqual(face_nodes, np.array([0, 1, 2, 2, 1, 3, 4]))
        self.assertArrayEqual(offset, np.array([3, 7]))

        matrix = np.array([[0, 1, 2, -999], [2, 1, -999, -999]])
        (face_nodes, offset) = utils.connectivity_matrix_as_array(matrix, -999)
        self.assertArrayEqual(face_nodes, np.array([0, 1, 2, 2, 1]))
        self.assertArrayEqual(offset, np.array([3, 5]))

    def test_equal_node_count(self):
        matrix = np.array([[0, 1, 2, 3], [2, 1, 3, 4]])
        (face_nodes, offset) = utils.connectivity_matrix_as_array(matrix, 999)
        self.assertArrayEqual(face_nodes, np.array([0, 1, 2, 3, 2, 1, 3, 4]))
        self.assertArrayEqual(offset, np.array([4, 8]))

    def test_one_face(self):
        matrix = np.array([[0, 1, 2, 3]])
        (face_nodes, offset) = utils.connectivity_matrix_as_array(matrix, 999)
        self.assertArrayEqual(face_nodes, np.array([0, 1, 2, 3]))
        self.assertArrayEqual(offset, np.array([4]))

    def test_empty_face(self):
        matrix = np.array([[0, 1], [999, 0]])
        with self.assertRaises(ValueError):
            utils.connectivity_matrix_as_array(matrix, 999)
