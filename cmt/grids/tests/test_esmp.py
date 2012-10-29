#! /usr/bin/env python import unittest

import unittest
from cmt.grids import (EsmpRasterField, EsmpRectilinear, EsmpStructured,
                       EsmpUnstructured, EsmpUniformRectilinear,
                       EsmpRectilinearField,
                       DimensionError)
from cmt.grids import run_regridding
import numpy as np

import ESMP

class TestEsmp (unittest.TestCase):

    @classmethod
    def setUpClass (cls):
        ESMP.ESMP_Initialize()

    @classmethod
    def tearDownClass (cls):
        ESMP.ESMP_Finalize()

    #@unittest.skip ('skip')
    def test_2d (self):
        # Create a grids that looks like this,
        #
        #
        #    (0) --- (1) --- (2)
        #     |       |       |
        #     |   0   |   1   |
        #     |       |       |
        #    (3) --- (4) --- (5)

        g = EsmpUnstructured ([0, 1, 2, 0, 1, 2], [0, 0, 0, 1, 1, 1],
                              [0, 1, 4, 3, 1, 2, 5, 4], [4, 8])
        g = EsmpStructured ([0, 1, 2, 0, 1, 2], [0, 0, 0, 1, 1, 1], (3, 2))

        # The as_mesh method provides a view of the grid as an ESMP_Mesh.

        cell_count = ESMP.ESMP_MeshGetLocalElementCount (g.as_mesh ())
        self.assertEqual (cell_count, 2)

        point_count = ESMP.ESMP_MeshGetLocalNodeCount (g.as_mesh ())
        self.assertEqual (point_count, 6)

        # ESMP elements are the same as the grids cells. Likewise with
        # nodes and points.

        g = EsmpRectilinear ([0, 1, 2], [0, 1])
        cell_count = ESMP.ESMP_MeshGetLocalElementCount (g.as_mesh ())
        self.assertEqual (cell_count, g.get_cell_count ())

        point_count = ESMP.ESMP_MeshGetLocalNodeCount (g.as_mesh ())
        self.assertEqual (point_count, g.get_point_count ())

        g = EsmpUniformRectilinear ([3, 2], [1., 1.], [0., 0.])

    #@unittest.skip ('skip')
    def test_raster (self):
        # Create a grids that looks like this,
        #
        #
        #    (0) --- (1) --- (2)
        #     |       |       |
        #     |   0   |   1   |
        #     |       |       |
        #    (3) --- (4) --- (5)

        # Create the field,

        g = EsmpRasterField ((3,2), (2,1), (0, 0))
        self.assert_cell_count (g, 2)
        self.assert_point_count (g, 6)

        # Add some data at the points of our grid.

        data = np.arange (6)
        g.add_field ('var0', data, centering='point')
        self.assert_field_values (g, 'var0', [0., 1., 2., 3., 4., 5.])
        self.assert_field_type (g, 'var0', np.dtype ('float64'))

        data = np.arange (6)
        data.shape = (2, 3)
        g.add_field ('var0', data, centering='point')
        self.assert_field_values (g, 'var0', [0., 1., 2., 3., 4., 5.])

        # If the size or shape doesn't match, it's an error.

        # DimensionError: 2 != 6
        with self.assertRaises (DimensionError):
            data = np.arange (2)
            g.add_field ('bad var', data, centering='point')

        # DimensionError: (3, 2) != (2, 3)
        with self.assertRaises (DimensionError):
            data = np.ones ((3, 2))
            g.add_field ('bad var', data, centering='point')

    #@unittest.skip ('skip')
    def test_mapper (self):
        from cmt.grids.raster import UniformRectilinear
        from cmt.grids.rectilinear import Rectilinear

        src = EsmpRasterField ((3,3), (1,1), (0, 0))
        data = np.arange (src.get_cell_count (), dtype=np.float64)
        src.add_field ('srcfield', data, centering='zonal')

        self.assert_point_count (src, 9)
        self.assert_cell_count (src, 4)

        self.assert_x (src, [0., 1., 2., 0., 1., 2., 0., 1., 2.])
        self.assert_y (src, [0., 0., 0., 1., 1., 1., 2., 2., 2.])

        self.assert_connectivity (src, [0, 1, 4, 3, 1, 2, 5, 4,
                                        3, 4, 7, 6, 4, 5, 8, 7])

        dst = EsmpRectilinearField ([0., .5, 1.5, 2.], [0., .5, 1.5, 2.])
        data = np.empty (dst.get_cell_count (), dtype=np.float64)
        dst.add_field ('dstfield', data, centering='zonal')

        self.assert_point_count (dst, 16)
        self.assert_cell_count (dst, 9)

        self.assert_x (dst, [0., 0.5, 1.5, 2., 0., 0.5, 1.5, 2.,
                             0., 0.5, 1.5, 2., 0., 0.5, 1.5, 2.])
        self.assert_y (dst, [0., 0., 0., 0., 0.5, 0.5, 0.5, 0.5,
                             1.5, 1.5, 1.5, 1.5, 2., 2., 2., 2.])
        self.assert_connectivity (dst, [ 0,  1,  5,  4,  1,  2,  6,  5,
                                         2,  3,  7,  6,  4,  5,  9,  8,
                                         5,  6, 10,  9,  6,  7, 11, 10,
                                         8,  9, 13, 12,  9, 10, 14, 13,
                                        10, 11, 15, 14])

        src_field = src.as_esmp ('srcfield')
        dst_field = dst.as_esmp ('dstfield')

        cell_count = ESMP.ESMP_MeshGetLocalElementCount (src.as_mesh ())
        point_count = ESMP.ESMP_MeshGetLocalNodeCount (src.as_mesh ())
        self.assertEqual (cell_count, 4)
        self.assertEqual (point_count, 9)

        local_cell_count = ESMP.ESMP_MeshGetLocalElementCount (
            dst.as_mesh ())
        local_point_count = ESMP.ESMP_MeshGetLocalNodeCount (
            dst.as_mesh ())
        self.assertEqual (local_cell_count, 9)
        self.assertEqual (local_point_count, 16)

        #>>> ESMP.ESMP_FieldPrint (src_field)
        #>>> ESMP.ESMP_FieldPrint (dst_field)

        f = run_regridding (src_field, dst_field)
        field_ptr = ESMP.ESMP_FieldGetPtr(f, 0)

    #@unittest.skip ('skip')
    def test_values_on_cells (self):
        (M, N) = (300, 300)
        src = EsmpRasterField ((M, N), (1, 1), (0, 0))

        (X, Y) = np.meshgrid (np.arange (0.5, 299.5, 1.),
                              np.arange (0.5, 299.5, 1.))

        data = np.sin (np.sqrt (X**2+Y**2)*np.pi/M)
        src.add_field ('srcfield', data, centering='zonal')

        dst = EsmpRasterField ((M*2-1, N*2-1), (1./2, 1./2), (0, 0))
        data = np.empty (dst.get_cell_count (), dtype=np.float64)
        dst.add_field ('dstfield', data, centering='zonal')

        src_field = src.as_esmp ('srcfield')
        dst_field = dst.as_esmp ('dstfield')

        f = run_regridding (src_field, dst_field)
        ans = ESMP.ESMP_FieldGetPtr(f, 0)

        (X, Y) = np.meshgrid (np.arange (0.5, 299.5, .5),
                              np.arange (0.5, 299.5, .5))
        exact = np.sin (np.sqrt (X**2+Y**2)*np.pi/M)
        residual = np.abs (exact.flat-ans)/(M*N*4.)
        self.assertAlmostEqual (np.sum (residual), 0., 2)

    #@unittest.skip ('skip')
    def test_values_on_points (self):
        (M, N) = (300, 300)
        src = EsmpRasterField ((M, N), (1, 1), (0, 0))

        (X, Y) = np.meshgrid (np.arange (0.5, 300.5, 1.),
                              np.arange (0.5, 300.5, 1.))
        data = np.sin (np.sqrt (X**2+Y**2)*np.pi/M)
        src.add_field ('srcfield_at_points', data, centering='point')

        dst = EsmpRasterField ((M*2-1, N*2-1), (1./2, 1./2), (0, 0))
        data = np.empty (dst.get_point_count (), dtype=np.float64)
        dst.add_field ('dstfield_at_points', data, centering='point')

        src_field = src.as_esmp ('srcfield_at_points')
        dst_field = dst.as_esmp ('dstfield_at_points')

        f = run_regridding (src_field, dst_field,
                            method=ESMP.ESMP_REGRIDMETHOD_BILINEAR)
        ans = ESMP.ESMP_FieldGetPtr(f, 0)

        (X, Y) = np.meshgrid (np.arange (0.5, 300., .5),
                              np.arange (0.5, 300., .5))
        exact = np.sin (np.sqrt (X**2+Y**2)*np.pi/M)
        residual = np.abs (exact.flat-ans)/(M*N*4.)
        self.assertAlmostEqual (np.sum (residual), 0., 3)

    def assert_field_type (self, field, name, expected_type):
        value = field.get_field (name)
        self.assertEqual (value.dtype, expected_type)
    def assert_field_values (self, field, name, expected_values):
        values = field.get_field (name)
        self.assertListEqual (list (values), list (expected_values))

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

def suite ():
    suite = unittest.TestLoader ().loadTestsFromTestCase (TestRasterGrid)
    return suite

if __name__ == '__main__':
    unittest.main ()

