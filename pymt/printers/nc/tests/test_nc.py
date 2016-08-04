#! /usr/bin/env python

import os
import unittest
import numpy as np
from numpy.testing import assert_array_equal

from cmt.grids import (RasterField, RectilinearField, StructuredField,
                       UnstructuredField)
from cmt.printers.nc.write import field_tofile


class NumpyArrayMixIn(object):
    def assertArrayEqual(self, actual, expected):
        try:
            assert_array_equal(actual, expected)
        except AssertionError as error:
            self.fail(error)


class AssertIsFileMixIn(object):
    def assertIsFile(self, file):
        import os
        if not os.path.isfile(file):
            self.fail('%s is not a regular file' % file)


class TempFileMixIn(object):
    def temp_file_name(self, **kwds):
        import tempfile, os
        if 'dir' not in kwds:
            kwds['dir'] = os.getcwd()

        (handle, name) = tempfile.mkstemp(**kwds)
        os.close(handle)
        os.remove(name)
        try:
            self._temp_files.append(name)
        except AttributeError:
            self._temp_files = [name]
        return name

    def tearDown(self):
        for file in self._temp_files:
            try:
                os.remove(file)
            except OSError:
                pass


class NetcdfMixIn(TempFileMixIn, unittest.TestCase, NumpyArrayMixIn,
             AssertIsFileMixIn):
    def assertDimensionsEqual(self, root, expected_keys):
        self.assertItemsEqual(expected_keys, root.dimensions.keys())

    def assertDataVariableNames(self, root, expected_names):
        self.assertItemsEqual(root.variables.keys(), expected_names)

    def assertDataVariableArrayEqual(self, root, var, expected_values):
        self.assertArrayEqual(expected_values, root.variables[var])

    def assertDataVariableUnitsEqual(self, root, var, expected_units):
        self.assertEqual(root.variables[var].units, expected_units)

    def assertDataVariableLongNameEqual(self, root, var, expected_name):
        self.assertEqual(root.variables[var].long_name, expected_name)

    @staticmethod
    def open_as_netcdf(file):
        import netCDF4 as nc4
        return nc4.Dataset(file, 'r', format='NETCDF4')


class TestUniformRectilinear(NetcdfMixIn):
    def test_0d(self):
        nc_file = self.temp_file_name(prefix='raster.0d.', suffix='.nc')
        field = RasterField((1, ), (0, ), (0, ), units=('m', ))

        attrs = dict(description='Example 0D nc file', author='Eric')
        for i in range(10):
            field.add_field('Elevation', i*10., centering='point')
            field_tofile(field, nc_file, attrs=attrs, append=True)

        self.assertIsFile(nc_file)

        root = self.open_as_netcdf(nc_file)

        self.assertDataVariableNames(root, ['mesh', 'Elevation', 'time'])
        self.assertDimensionsEqual(root, ['time'])

        self.assertDataVariableLongNameEqual(root, 'Elevation', 'Elevation')
        self.assertDataVariableUnitsEqual(root, 'Elevation', '-')

        self.assertDataVariableArrayEqual(root, 'Elevation', 10.*np.arange(10))
        self.assertDataVariableArrayEqual(root, 'time', range(10))

        root.close()

    def test_2d(self):
        nc_file = self.temp_file_name(prefix='raster.2d.', suffix='.nc')
        field = RasterField((3,2), (2.,1), (0,0.5), units=('m', 'km'))

        data = np.arange(6.)

        field.add_field('Temperature', data*10, centering='point', units='C')
        field.add_field('Elevation', data, centering='point', units='meters')
        field.add_field('Velocity', data*100, centering='point', units='m/s')
        field.add_field('Temp', data*2, centering='point', units='F')

        attrs = dict(description='Example nc file', author='Eric')
        field_tofile(field, nc_file, attrs=attrs, append=True)

        self.assertTrue(os.path.isfile(nc_file))

        root = self.open_as_netcdf(nc_file)
        self.assertDataVariableNames(root, ['mesh', 'Temperature', 'Elevation',
                                     'Velocity', 'Temp',
                                     'x', 'y', 'time'])
        self.assertDimensionsEqual(root, ['x', 'y', 'time'])
        self.assertDataVariableArrayEqual(root, 'x', [.5, 1.5])
        self.assertDataVariableArrayEqual(root, 'y', [0., 2., 4.])

        for name in ['Temperature', 'Elevation', 'Velocity', 'Temp']:
            self.assertDataVariableLongNameEqual(root, name, name)

        for (name, units) in [('Temperature', 'C'), ('Elevation', 'meters'),
                              ('Velocity', 'm/s'), ('Temp', 'F')]:
            self.assertDataVariableUnitsEqual(root, name, units)

        root.close()

    def test_3d(self):
        nc_file = self.temp_file_name(prefix='raster.3d.', suffix='.nc')

        field = RasterField((2, 3, 4), (1, 2, 3), (-1, 0, 1),
                            indexing='ij', units=('mm', 'm', 'km'))

        data = np.arange(24.)
        field.add_field('Temperature', data*10, centering='point', units='C')
        field.add_field('Elevation', data, centering='point', units='meters')
        field.add_field('Velocity', data*100, centering='point', units='m/s')
        field.add_field('Temp', data*2, centering='point', units='F')

        attrs = dict(description='Example 3D nc file', author='Eric')
        field_tofile(field, nc_file, attrs=attrs, append=True)

        self.assertIsFile(nc_file)

    def test_1d(self):
        nc_file = self.temp_file_name(prefix='raster.1d.', suffix='.nc')
        field = RasterField((12, ), (1, ), (-1, ), units=('m', ))
        data = np.arange(12.)
        field.add_field('Elevation', data, centering='point')

        attrs = dict(description='Example 1D nc file', author='Eric')
        field_tofile(field, nc_file, attrs=attrs, append=True)

        self.assertIsFile(nc_file)

        root = self.open_as_netcdf(nc_file)
        self.assertDataVariableNames(root, ['mesh', 'Elevation', 'x', 'time'])
        self.assertDimensionsEqual(root, ['x', 'time'])
        self.assertDataVariableArrayEqual(root, 'x', np.arange (12.) - 1.)

        self.assertDataVariableLongNameEqual(root, 'Elevation', 'Elevation')
        self.assertDataVariableUnitsEqual(root, 'Elevation', '-')

        self.assertDataVariableUnitsEqual(root, 'x', 'm')
        root.close()


class TestRectilinear(NetcdfMixIn):
    def test_1d(self):
        nc_file = self.temp_file_name(prefix='rectilinear.1d.', suffix='.nc')

        field = RectilinearField((1, 2, 4, 5), units=('m', ))
        data = np.arange(4.)
        field.add_field('Elevation', data, centering='point')

        attrs = dict(description='Example 1D nc file', author='Eric')
        field_tofile(field, nc_file, attrs=attrs, append=True)

        self.assertIsFile(nc_file)

        root = self.open_as_netcdf(nc_file)
        self.assertDataVariableNames(root, ['mesh', 'Elevation', 'x', 'time'])
        self.assertDimensionsEqual(root, ['x', 'time'])
        self.assertDataVariableArrayEqual(root, 'x', [1, 2, 4, 5])

        self.assertDataVariableLongNameEqual(root, 'Elevation', 'Elevation')
        self.assertDataVariableUnitsEqual(root, 'Elevation', '-')

        self.assertDataVariableUnitsEqual(root, 'x', 'm')
        root.close()

    def test_2d(self):
        nc_file = self.temp_file_name(prefix='rectilinear.2d.', suffix='.nc')

        field = RectilinearField((1, 4, 5), (2, 3),
                                 units=('degrees_north', 'degrees_east'),
                                 coordinate_names=['latitude', 'longitude'])

        data = np.arange(6.)

        field.add_field('Temperature', data*10, centering='point', units='C')
        field.add_field('Elevation', data, centering='point', units='meters')
        field.add_field('Velocity', data*100, centering='point', units='m/s')
        field.add_field('Temp', data*2, centering='point', units='F')

        attrs = dict(description='Example nc file', author='Eric')
        field_tofile(field, nc_file, attrs=attrs, append=True)

        self.assertTrue(os.path.isfile(nc_file))

        root = self.open_as_netcdf(nc_file)
        self.assertDataVariableNames(root,
                              ['mesh', 'Temperature', 'Elevation', 'Velocity',
                               'Temp', 'longitude', 'latitude', 'time'])
        self.assertDimensionsEqual(root, [ 'longitude', 'latitude', 'time'])
        self.assertDataVariableArrayEqual(root, 'longitude', [2., 3.])
        self.assertDataVariableArrayEqual(root, 'latitude', [1., 4., 5.])
        self.assertDataVariableLongNameEqual(root, 'longitude', 'longitude')
        self.assertDataVariableLongNameEqual(root, 'latitude', 'latitude')
        self.assertDataVariableUnitsEqual(root, 'longitude', 'degrees_east')
        self.assertDataVariableUnitsEqual(root, 'latitude', 'degrees_north')

        for name in ['Temperature', 'Elevation', 'Velocity', 'Temp']:
            self.assertDataVariableLongNameEqual(root, name, name)
        for (v, u) in dict(Temperature='C', Elevation='meters',
                           Velocity='m/s', Temp='F').items():
            self.assertDataVariableUnitsEqual(root, v, u)
        root.close()


class TestStructured(NetcdfMixIn):
    def test_1d (self):
        nc_file = self.temp_file_name(prefix='structured.1d.', suffix='.nc')

        field = StructuredField ((1, 2, 4, 5), (4, ), indexing='ij', units=('m', ))
        data = np.arange (4.)
        field.add_field ('Elevation', data, centering='point')

        attrs = dict (description='Example 1D nc file', author='Eric')
        field_tofile (field, nc_file, attrs=attrs, append=True)

        self.assertTrue (os.path.isfile (nc_file))

        try:
            root = self.open_as_netcdf (nc_file)
        except Exception:
            raise AssertionError ('%s: Could not open' % nc_file)
        else:
            self.assertDataVariableNames (root, ['mesh', 'Elevation', 'x', 'time'])
            self.assertDimensionsEqual (root, ['x', 'time'])
            self.assertDataVariableArrayEqual (root, 'x', [1, 2, 4, 5])

            self.assertDataVariableLongNameEqual (root, 'Elevation', 'Elevation')
            self.assertDataVariableUnitsEqual (root, 'Elevation', '-')

            self.assertDataVariableUnitsEqual (root, 'x', 'm')
        finally:
            root.close ()

    def test_2d (self):
        nc_file = self.temp_file_name(prefix='structured.2d.', suffix='.nc')

        field = StructuredField((1, 1, 4, 4, 5, 5), (2, 3, 2, 3, 2, 3), (3, 2),
                                indexing='ij', units=('m', 'km'))

        data = np.arange(6.)

        field.add_field('Temperature', data * 10, centering='point', units='C')
        field.add_field('Elevation', data, centering='point', units='meters')
        field.add_field('Velocity', data * 100, centering='point', units='m/s')
        field.add_field('Temp', data * 2, centering='point', units='F')

        attrs = dict(description='Example nc file', author='Eric')
        field_tofile(field, nc_file, attrs=attrs, append=True)

        self.assertTrue(os.path.isfile (nc_file))

        try:
            root = self.open_as_netcdf(nc_file)
        except Exception:
            raise AssertionError('%s: Could not open' % nc_file)
        else:
            self.assertDataVariableNames(root, ['mesh', 'Temperature', 'Elevation',
                                         'Velocity', 'Temp',
                                         'x', 'y', 'time'])
            self.assertDimensionsEqual(root, ['x', 'y', 'time'])
            self.assertDataVariableArrayEqual(root, 'x', np.array([[2., 3.],
                                                        [2., 3.],
                                                        [2., 3.]]))
            self.assertDataVariableArrayEqual(root, 'y', np.array([[1., 1.],
                                                        [4., 4.],
                                                        [5., 5.]]))

            for name in ['Temperature', 'Elevation', 'Velocity', 'Temp']:
                self.assertDataVariableLongNameEqual(root, name, name)
            for (v, u) in dict(Temperature='C', Elevation='meters',
                               Velocity='m/s', Temp='F').items ():
                self.assertDataVariableUnitsEqual(root, v, u)
        finally:
            root.close()


class TestUnstructured(NetcdfMixIn):
    def test_1d(self):
        nc_file = self.temp_file_name(prefix='unstructured.1d.', suffix='.ncu')

        field = UnstructuredField([0, 1, 4, 10], [0, 1, 1, 2, 2, 3],
                                  [2, 4, 6], units=('m', ))

        field.add_field('point_field', np.arange (4), centering='point',
                        units='C')
        field.add_field('cell_field', np.arange (3)*10. , centering='zonal',
                        units='F')

        field_tofile(field, nc_file, append=False)

        self.assertIsFile(nc_file)

    def test_2d (self):
        nc_file = self.temp_file_name(prefix='unstructured.2d.', suffix='.ncu')

        field = UnstructuredField([0, 0, 1, 1], [0, 2, 1, 3],
                                  [0, 2, 1, 2, 3, 1], [3, 6],
                                  units=('m', 'm'))

        data = np.arange(4)
        field.add_field('point_field', data, centering='point', units='m')

        data = np.arange(2)
        field.add_field('cell_field', data, centering='zonal',
                        units='m^2')

        field_tofile(field, nc_file, append=False)

        root = self.open_as_netcdf(nc_file)

        self.assertDataVariableNames(
            root, ['mesh', 'point_field', 'cell_field', 'node_x', 'node_y',
                   'time', 'face_nodes', 'face_nodes_offset',
                   'face_nodes_connectivity'])
        self.assertDimensionsEqual(root, ['n_face', 'n_node', 'n_vertex',
                                          'n_max_face_nodes', 'time'])
        self.assertDataVariableArrayEqual(root, 'node_x', [0., 2., 1., 3.])
        self.assertDataVariableArrayEqual(root, 'node_y', [0., 0., 1., 1.])
        self.assertDataVariableArrayEqual(root, 'face_nodes_offset', [3, 6])
        self.assertDataVariableArrayEqual(root, 'face_nodes',
                                          np.array([[0, 2, 1], [2, 3, 1]]))

        self.assertDataVariableLongNameEqual(root, 'point_field', 'point_field')
        self.assertDataVariableLongNameEqual(root, 'cell_field', 'cell_field')
        self.assertDataVariableUnitsEqual(root, 'point_field', 'm')
        self.assertDataVariableUnitsEqual(root, 'cell_field', 'm^2')

        root.close()

if __name__ == '__main__':
    unittest.main()
