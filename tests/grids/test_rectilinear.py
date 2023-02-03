import unittest

import numpy as np

from pymt.grids import Rectilinear, RectilinearPoints

from ..grids.test_utils import NumpyArrayMixIn


class TestRectilinearGrid(unittest.TestCase):
    def assert_point_count(self, grid, point_count):
        self.assertEqual(point_count, grid.get_point_count())

    def assert_cell_count(self, grid, cell_count):
        self.assertEqual(cell_count, grid.get_cell_count())

    def assert_shape(self, grid, shape):
        self.assertListEqual(list(grid.get_shape()), list(shape))

    def assert_spacing(self, grid, spacing):
        self.assertListEqual(list(grid.get_spacing()), list(spacing))

    def assert_origin(self, grid, origin):
        self.assertListEqual(list(grid.get_origin()), list(origin))

    def assert_x(self, grid, x):
        self.assertListEqual(list(x), list(grid.get_x()))

    def assert_y(self, grid, y):
        self.assertListEqual(list(y), list(grid.get_y()))

    def assert_z(self, grid, z):
        self.assertListEqual(list(z), list(grid.get_z()))

    def assert_offset(self, grid, offset):
        self.assertListEqual(list(offset), list(grid.get_offset()))

    def assert_connectivity(self, grid, connectivity):
        self.assertListEqual(list(connectivity), list(grid.get_connectivity()))

    @unittest.skip("xy indexing is deprecated")
    def test_xy_indexing(self):
        grid = Rectilinear([1.0, 2.0, 4.0, 8.0], [1.0, 2.0, 3.0])
        self.assert_point_count(grid, 12)
        self.assert_cell_count(grid, 6)
        self.assert_shape(grid, (3, 4))
        self.assert_x(
            grid, [1.0, 2.0, 4.0, 8.0, 1.0, 2.0, 4.0, 8.0, 1.0, 2.0, 4.0, 8.0]
        )
        self.assert_y(
            grid, [1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 3.0]
        )

    def test_ij_indexing(self):
        grid = Rectilinear([1.0, 2.0, 4.0, 8.0], [1.0, 2.0, 3.0], indexing="ij")
        self.assert_point_count(grid, 12)
        self.assert_cell_count(grid, 6)
        self.assert_shape(grid, (4, 3))
        self.assert_x(
            grid, [1.0, 2.0, 3.0, 1.0, 2.0, 3.0, 1.0, 2.0, 3.0, 1.0, 2.0, 3.0]
        )
        self.assert_y(
            grid, [1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 4.0, 4.0, 4.0, 8.0, 8.0, 8.0]
        )
        self.assert_connectivity(
            grid,
            [0, 1, 4, 3, 1, 2, 5, 4, 3, 4, 7, 6, 4, 5, 8, 7, 6, 7, 10, 9, 7, 8, 11, 10],
        )

    def test_grid_of_points(self):
        grid = RectilinearPoints(
            [1.0, 2.0, 4.0, 8.0], [1.0, 2.0, 3.0], indexing="ij", set_connectivity=True
        )
        self.assert_point_count(grid, 12)
        self.assert_cell_count(grid, 0)
        self.assert_shape(grid, (4, 3))
        self.assert_x(
            grid, [1.0, 2.0, 3.0, 1.0, 2.0, 3.0, 1.0, 2.0, 3.0, 1.0, 2.0, 3.0]
        )
        self.assert_y(
            grid, [1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 4.0, 4.0, 4.0, 8.0, 8.0, 8.0]
        )
        self.assert_connectivity(grid, np.arange(grid.get_point_count()))
        self.assert_offset(grid, np.arange(1, grid.get_point_count() + 1))

    def test_1d_grid(self):
        grid = Rectilinear([1, 3, 4, 5, 6], set_connectivity=True)
        self.assert_point_count(grid, 5)
        self.assert_cell_count(grid, 4)
        self.assert_shape(grid, (5,))
        self.assert_x(grid, [1.0, 3.0, 4.0, 5.0, 6.0])
        # self.assert_y (grid, [0., 0., 0., 0., 0.])
        self.assert_connectivity(grid, [0, 1, 1, 2, 2, 3, 3, 4])
        self.assert_offset(grid, [2, 4, 6, 8])

    @unittest.skip("xy indexing is deprecated")
    def test_3d_xy_indexing(self):
        grid = Rectilinear(
            [0, 1, 2, 3], [4, 5, 6], [7, 8], set_connectivity=True, indexing="xy"
        )
        self.assert_point_count(grid, 24)
        self.assert_cell_count(grid, 6)
        self.assert_shape(grid, (2, 3, 4))
        self.assert_x(
            grid,
            [
                0.0,
                1.0,
                2.0,
                3.0,
                0.0,
                1.0,
                2.0,
                3.0,
                0.0,
                1.0,
                2.0,
                3.0,
                0.0,
                1.0,
                2.0,
                3.0,
                0.0,
                1.0,
                2.0,
                3.0,
                0.0,
                1.0,
                2.0,
                3.0,
            ],
        )
        self.assert_y(
            grid,
            [
                4.0,
                4.0,
                4.0,
                4.0,
                5.0,
                5.0,
                5.0,
                5.0,
                6.0,
                6.0,
                6.0,
                6.0,
                4.0,
                4.0,
                4.0,
                4.0,
                5.0,
                5.0,
                5.0,
                5.0,
                6.0,
                6.0,
                6.0,
                6.0,
            ],
        )
        self.assert_z(
            grid,
            [
                7.0,
                7.0,
                7.0,
                7.0,
                7.0,
                7.0,
                7.0,
                7.0,
                7.0,
                7.0,
                7.0,
                7.0,
                8.0,
                8.0,
                8.0,
                8.0,
                8.0,
                8.0,
                8.0,
                8.0,
                8.0,
                8.0,
                8.0,
                8.0,
            ],
        )
        self.assert_offset(grid, 8.0 * np.arange(1, grid.get_cell_count() + 1))

    def test_3d_ij_indexing(self):
        grid = Rectilinear(
            [0, 1, 2, 3], [4, 5, 6], [7, 8], set_connectivity=True, indexing="ij"
        )
        self.assert_point_count(grid, 24)
        self.assert_cell_count(grid, 6)
        self.assert_shape(grid, (4, 3, 2))
        self.assert_x(
            grid,
            [
                7.0,
                8.0,
                7.0,
                8.0,
                7.0,
                8.0,
                7.0,
                8.0,
                7.0,
                8.0,
                7.0,
                8.0,
                7.0,
                8.0,
                7.0,
                8.0,
                7.0,
                8.0,
                7.0,
                8.0,
                7.0,
                8.0,
                7.0,
                8.0,
            ],
        )
        self.assert_y(
            grid,
            [
                4.0,
                4.0,
                5.0,
                5.0,
                6.0,
                6.0,
                4.0,
                4.0,
                5.0,
                5.0,
                6.0,
                6.0,
                4.0,
                4.0,
                5.0,
                5.0,
                6.0,
                6.0,
                4.0,
                4.0,
                5.0,
                5.0,
                6.0,
                6.0,
            ],
        )
        self.assert_z(
            grid,
            [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                2.0,
                2.0,
                2.0,
                2.0,
                2.0,
                2.0,
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
                3.0,
            ],
        )
        self.assert_offset(grid, 8.0 * np.arange(1, grid.get_cell_count() + 1))


class TestRectilinearGridUnits(unittest.TestCase):
    def test_2d_units_ij_indexing_by_name(self):
        grid = Rectilinear(
            [1.0, 2.0, 4.0, 8.0],
            [1.0, 2.0, 3.0],
            indexing="ij",
            units=["y_units", "x_units"],
        )

        self.assertEqual(grid.get_x_units(), "x_units")
        self.assertEqual(grid.get_y_units(), "y_units")

    @unittest.skip("xy indexing is deprecated")
    def test_2d_units_xy_indexing_by_name(self):
        grid = Rectilinear(
            [1.0, 2.0, 4.0, 8.0],
            [1.0, 2.0, 3.0],
            indexing="xy",
            units=["x_units", "y_units"],
        )

        self.assertEqual(grid.get_x_units(), "x_units")
        self.assertEqual(grid.get_y_units(), "y_units")

    def test_2d_units_ij_indexing_by_coordinate(self):
        grid = Rectilinear(
            [1.0, 2.0, 4.0, 8.0],
            [1.0, 2.0, 3.0],
            indexing="ij",
            units=["y_units", "x_units"],
        )

        self.assertEqual(grid.get_coordinate_units(0), "y_units")
        self.assertEqual(grid.get_coordinate_units(1), "x_units")

    @unittest.skip("xy indexing is deprecated")
    def test_2d_units_xy_indexing_by_coordinate(self):
        grid = Rectilinear(
            [1.0, 2.0, 4.0, 8.0],
            [1.0, 2.0, 3.0],
            indexing="ij",
            units=["y_units", "x_units"],
        )

        self.assertEqual(grid.get_coordinate_units(0), "x_units")
        self.assertEqual(grid.get_coordinate_units(1), "y_units")


class TestRectilinearGridCoordinateNames(unittest.TestCase):
    def test_2d_coordinate_name_ij_default(self):
        grid = Rectilinear([1.0, 2.0, 4.0, 8.0], [1.0, 2.0, 3.0], indexing="ij")

        self.assertEqual(grid.get_coordinate_name(0), "y")
        self.assertEqual(grid.get_coordinate_name(1), "x")

    @unittest.skip("xy indexing is deprecated")
    def test_2d_coordinate_name_xy_default(self):
        grid = Rectilinear([1.0, 2.0, 4.0, 8.0], [1.0, 2.0, 3.0], indexing="xy")

        self.assertEqual(grid.get_coordinate_name(0), "x")
        self.assertEqual(grid.get_coordinate_name(1), "y")

    def test_2d_coordinate_name_ij_indexing(self):
        grid = Rectilinear(
            [1.0, 2.0, 4.0, 8.0],
            [1.0, 2.0, 3.0],
            indexing="ij",
            coordinate_names=["longitude", "latitude"],
        )

        self.assertEqual(grid.get_coordinate_name(0), "longitude")
        self.assertEqual(grid.get_coordinate_name(1), "latitude")

    @unittest.skip("xy indexing is deprecated")
    def test_2d_coordinate_name_xy_indexing(self):
        grid = Rectilinear(
            [1.0, 2.0, 4.0, 8.0],
            [1.0, 2.0, 3.0],
            indexing="xy",
            coordinate_names=["latitude", "longitude"],
        )

        self.assertEqual(grid.get_coordinate_name(0), "latitude")
        self.assertEqual(grid.get_coordinate_name(1), "longitude")

    def test_2d_coordinate_name_ij_indexing_with_kwds(self):
        grid = Rectilinear(
            [1.0, 2.0, 4.0, 8.0],
            [1.0, 2.0, 3.0],
            indexing="ij",
            coordinate_names=["latitude", "longitude"],
        )

        self.assertEqual(grid.get_coordinate_name(0), "latitude")
        self.assertEqual(grid.get_coordinate_name(1), "longitude")

        # self.assertEqual (grid.get_coordinate_name (0, indexing='xy'), 'longitude')
        # self.assertEqual (grid.get_coordinate_name (1, indexing='xy'), 'latitude')


class TestRectilinearGridCoordinates(unittest.TestCase, NumpyArrayMixIn):
    def test_2d_coordinates_ij_default(self):
        grid = Rectilinear([1.0, 2.0, 4.0, 8.0], [1.0, 2.0, 3.0], indexing="ij")

        self.assertArrayEqual(
            grid.get_point_coordinates(axis=0),
            np.array([1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 4.0, 4.0, 4.0, 8.0, 8.0, 8.0]),
        )
        self.assertArrayEqual(
            grid.get_point_coordinates(axis=1), np.array([1.0, 2.0, 3.0] * 4)
        )

    @unittest.skip("xy indexing is deprecated")
    def test_2d_coordinates_xy_default(self):
        grid = Rectilinear([1.0, 2.0, 4.0, 8.0], [1.0, 2.0, 3.0], indexing="xy")

        self.assertTrue(
            np.allclose(
                grid.get_point_coordinates(axis=0), np.array([1.0, 2.0, 4.0, 8.0] * 3)
            )
        )
        self.assertTrue(
            np.allclose(
                grid.get_point_coordinates(axis=1),
                np.tile([1.0, 2.0, 3.0], (4, 1)).T.flat,
            )
        )

    def test_2d_coordinates_ij_indexing_with_kwds(self):
        grid = Rectilinear([1.0, 2.0, 4.0, 8.0], [1.0, 2.0, 3.0], indexing="ij")

        # self.assertTrue (np.allclose (grid.get_point_coordinates (axis=0, indexing='xy'),
        #                              np.array ([1., 2., 3.] * 4)))
        # self.assertTrue (np.allclose (grid.get_point_coordinates (axis=1, indexing='xy'),
        #                              np.tile ([1., 2., 4., 8.], (3, 1)).T.flat))

        self.assertTrue(
            np.allclose(
                grid.get_point_coordinates(axis=0, indexing="ij"),
                np.tile([1.0, 2.0, 4.0, 8.0], (3, 1)).T.flat,
            )
        )
        self.assertTrue(
            np.allclose(
                grid.get_point_coordinates(axis=1, indexing="ij"),
                np.array([1.0, 2.0, 3.0] * 4),
            )
        )


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRectilinearGrid)
    return suite


if __name__ == "__main__":
    unittest.main()
