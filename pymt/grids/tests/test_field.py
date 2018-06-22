#! /usr/bin/env python

import unittest
from pymt.grids import RasterField, DimensionError
import numpy as np


class TestRasterField(unittest.TestCase):
    def assert_field_values(self, field, name, expected_values):
        values = field.get_field(name)
        self.assertListEqual(list(values), list(expected_values))

    def test_2d_point_fields(self):
        # Create a field that looks like this,
        #
        #    (0) --- (1) --- (2)
        #     |       |       |
        #     |   0   |   1   |
        #     |       |       |
        #    (3) --- (4) --- (5)

        g = RasterField((2, 3), (1, 2), (0, 0), indexing="ij")

        data = np.arange(6)
        g.add_field("point_var_1", data, centering="point")
        g.add_field("point_var_2", data * 2, centering="point")

        data = np.arange(2)
        g.add_field("cell_var", data, centering="zonal")

        fields = g.get_point_fields()
        self.assertEqual(len(fields), 2)
        self.assertTrue("point_var_1" in fields)
        self.assertTrue("point_var_2" in fields)

        self.assert_field_values(g, "point_var_1", [0, 1, 2, 3, 4, 5])
        self.assert_field_values(g, "point_var_2", [0, 2, 4, 6, 8, 10])

    def test_2d_cell_fields(self):
        # Create a field that looks like this,
        #
        #    (0) --- (1) --- (2)
        #     |       |       |
        #     |   0   |   1   |
        #     |       |       |
        #    (3) --- (4) --- (5)

        g = RasterField((2, 3), (1, 2), (0, 0), indexing="ij")

        data = np.arange(6)
        g.add_field("point_var_1", data, centering="point")
        g.add_field("point_var_2", data * 2, centering="point")

        data = np.arange(2)
        g.add_field("cell_var_1", data, centering="zonal")
        g.add_field("cell_var_2", data * 2, centering="zonal")

        fields = g.get_cell_fields()
        self.assertEqual(len(fields), 2)
        self.assertTrue("cell_var_1" in fields)
        self.assertTrue("cell_var_2" in fields)

        self.assert_field_values(g, "cell_var_1", [0, 1])
        self.assert_field_values(g, "cell_var_2", [0, 2])

    def test_2d(self):
        # Create a field that looks like this,
        #
        #    (0) --- (1) --- (2)
        #     |       |       |
        #     |   0   |   1   |
        #     |       |       |
        #    (3) --- (4) --- (5)

        g = RasterField((2, 3), (1, 2), (0, 0), indexing="ij")

        self.assert_cell_count(g, 2)
        self.assert_point_count(g, 6)

        data = np.arange(6)
        g.add_field("var0", data, centering="point")

        self.assert_field_values(g, "var0", [0, 1, 2, 3, 4, 5])

        data = np.arange(6)
        data.shape = (2, 3)
        g.add_field("var0", data, centering="point")
        self.assert_field_values(g, "var0", [0, 1, 2, 3, 4, 5])

        # If the size or shape doesn't match, it's an error.
        with self.assertRaises(DimensionError):
            data = np.arange(2)
            g.add_field("bad var", data, centering="point")

        # DimensionError: (3, 2) != (2, 3)
        with self.assertRaises(DimensionError):
            data = np.ones((3, 2))
            g.add_field("bad var", data, centering="point")

        data = np.arange(2)
        g.add_field("var1", data, centering="zonal")
        self.assert_field_values(g, "var1", [0., 1.])

        # DimensionError: (2, 1) != (1, 2)
        with self.assertRaises(DimensionError):
            data = np.ones((2, 1))
            g.add_field("bad var", data, centering="zonal")

        # DimensionError: 3 != 2
        with self.assertRaises(DimensionError):
            data = np.arange(3)
            g.add_field("bad var", data, centering="zonal")

        # DimensionError: 1 != 2
        with self.assertRaises(DimensionError):
            data = np.array(3)
            g.add_field("bad var", data, centering="zonal")

    def test_raster_field_1d(self):
        g = RasterField((6,), (1.5,), (0.5,), indexing="ij")
        self.assert_point_count(g, 6)
        self.assert_cell_count(g, 5)

        point_data = np.arange(6.)
        g.add_field("Point Data", point_data, centering="point")

        cell_data = np.arange(5.) * 10.
        g.add_field("Cell Data", cell_data, centering="zonal")

        self.assert_field_values(g, "Cell Data", [0., 10., 20., 30., 40.])
        self.assert_field_values(g, "Point Data", [0., 1., 2., 3., 4., 5.])

    def test_raster_field_3d(self):
        g = RasterField((4, 3, 2), (1.5, 1., 3), (0.5, 0, -.5), indexing="ij")
        self.assert_point_count(g, 24)
        self.assert_cell_count(g, 6)

        g.add_field("Point Data", g.get_x(), centering="point")

        cell_data = np.arange(6.) * 10.
        g.add_field("Cell Data", cell_data, centering="zonal")

        g.get_field("Cell Data")
        self.assert_field_values(g, "Cell Data", [0., 10., 20., 30., 40., 50.])

        self.assert_field_values(
            g,
            "Point Data",
            [
                -0.5,
                2.5,
                -0.5,
                2.5,
                -0.5,
                2.5,
                -0.5,
                2.5,
                -0.5,
                2.5,
                -0.5,
                2.5,
                -0.5,
                2.5,
                -0.5,
                2.5,
                -0.5,
                2.5,
                -0.5,
                2.5,
                -0.5,
                2.5,
                -0.5,
                2.5,
            ],
        )

        self.assert_shape(g, (4, 3, 2))

        x = g.get_x()
        data = g.get_field("Point Data")

        self.assertEqual(x.size, data.size)

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


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRasterField)
    return suite


if __name__ == "__main__":
    unittest.main()
