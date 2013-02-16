#! /usr/bin/env python

import os
import unittest
import numpy as np

from cmt.grids import (RasterField, RectilinearField, StructuredField,
                       UnstructuredField)
from cmt.nc import field_tofile

class TestNc (unittest.TestCase):
    def setUp (self):
        for file in self.nc_files.values ():
            try:
                os.remove (file)
            except OSError:
                pass

    def tearDown (self):
        for file in self.nc_files.values ():
            try:
                os.remove (file)
            except OSError:
                pass

    def assert_dimension_keys (self, root, expected_keys):
        keys = root.dimensions.keys ()
        self.assertItemsEqual (expected_keys, keys)

    def assert_var_names (self, root, expected_names):
        vars = root.variables
        self.assertItemsEqual (vars.keys (), expected_names)
    def assert_var_values (self, root, var, expected_values):
        vars = root.variables
        values = vars[var][:]
        self.assertListEqual (list (values), list (expected_values))
    def assert_var_name (self, root, var, expected_name):
        vars = root.variables
        name = vars[var].long_name
        self.assertEqual (name, expected_name)
    def assert_var_units (self, root, var, expected_units):
        vars = root.variables
        units = vars[var].units
        self.assertEqual (units, expected_units)
    def assert_var_long_name (self, root, var, expected_long_name):
        vars = root.variables
        long_name = vars[var].long_name
        self.assertEqual (long_name, expected_long_name)

    @staticmethod
    def open_nc_file (file):
        import netCDF4 as nc
        return nc.Dataset (file, 'r', format='NETCDF4')


class TestUniformRectilinear (TestNc):
    nc_files = dict (
        test_0d='test-0d-00.nc',
        test_1d='test-1d-00.nc',
        test_2d='test-2d-00.nc',
        test_3d='test-3d-00.nc',
        test_2d_unstructured='test-2d-00.ncu',
    )

    def test_0d (self):
        nc_file = self.nc_files['test_0d']
        field = RasterField ((1, ), (0, ), (0, ), indexing='ij', units=('m', ))

        attrs = dict (description='Example 0D nc file', author='Eric')
        for i in range (10):
            field.add_field ('Elevation', i*10., centering='point')
            field_tofile (field, nc_file, attrs=attrs, append=True)

        self.assertTrue (os.path.isfile (nc_file))

        try:
            root = self.open_nc_file (nc_file)
        except Exception:
            raise AssertionError ('%s: Could not open' % nc_file)
        else:
            self.assert_var_names (root, ['Elevation', 't', 'dummy'])
            self.assert_dimension_keys (root, ['nt'])

            self.assert_var_name (root, 'Elevation', 'Elevation')
            self.assert_var_units (root, 'Elevation', '-')

            self.assert_var_values (root, 'Elevation', 10.*np.arange (10))
            self.assert_var_values (root, 't', range (10))
        finally:
            root.close ()

    def test_2d (self):
        nc_file = self.nc_files['test_2d']
        field = RasterField ((3,2), (2.,1), (0,0.5),
                             indexing='ij', units=('m', 'km'))

        data = np.arange (6.)

        field.add_field ('Temperature', data*10, centering='point', units='C')
        field.add_field ('Elevation', data, centering='point', units='meters')
        field.add_field ('Velocity', data*100, centering='point', units='m/s')
        field.add_field ('Temp', data*2, centering='point', units='F')

        attrs = dict (description='Example nc file', author='Eric')
        field_tofile (field, nc_file, attrs=attrs, append=True)

        self.assertTrue (os.path.isfile (nc_file))

        try:
            root = self.open_nc_file (nc_file)
        except Exception:
            raise AssertionError ('%s: Could not open' % nc_file)
        else:
            self.assert_var_names (root, ['Temperature', 'Elevation',
                                          'Velocity', 'Temp',
                                          'x', 'y', 't', 'dummy'])
            self.assert_dimension_keys (root, ['n_points', 'n_cells', 'n_vertices', 'nx', 'ny', 'nt'])
            self.assert_var_values (root, 'x', [.5, 1.5])
            self.assert_var_values (root, 'y', [0., 2., 4.])

            for name in ['Temperature', 'Elevation', 'Velocity', 'Temp']:
                self.assert_var_name (root, name, name)
            for (v, u) in dict (Temperature='C', Elevation='meters',
                                Velocity='m/s', Temp='F').items ():
                self.assert_var_units (root, v, u)
        finally:
            root.close ()

    def test_3d (self):
        nc_file = self.nc_files['test_3d']

        field = RasterField ((2, 3, 4), (1, 2, 3), (-1, 0, 1),
                             indexing='ij', units=('mm', 'm', 'km'))

        data = np.arange (24.)
        field.add_field ('Temperature', data*10, centering='point', units='C')
        field.add_field ('Elevation', data, centering='point', units='meters')
        field.add_field ('Velocity', data*100, centering='point', units='m/s')
        field.add_field ('Temp', data*2, centering='point', units='F')

        attrs = dict (description='Example 3D nc file', author='Eric')
        field_tofile (field, nc_file, attrs=attrs, append=True)

        self.assertTrue (os.path.isfile (nc_file))

    def test_1d (self):
        nc_file = self.nc_files['test_1d']
        field = RasterField ((12, ), (1, ), (-1, ), indexing='ij', units=('m', ))
        data = np.arange (12.)
        field.add_field ('Elevation', data, centering='point')

        attrs = dict (description='Example 1D nc file', author='Eric')
        field_tofile (field, nc_file, attrs=attrs, append=True)

        self.assertTrue (os.path.isfile (nc_file))

        try:
            root = self.open_nc_file (nc_file)
        except Exception:
            raise AssertionError ('%s: Could not open' % nc_file)
        else:
            self.assert_var_names (root, ['Elevation', 'x', 't', 'dummy'])
            self.assert_dimension_keys (root, ['n_points', 'n_cells', 'n_vertices', 'nx', 'nt'])
            self.assert_var_values (root, 'x', np.arange (12.) - 1.)

            self.assert_var_name (root, 'Elevation', 'Elevation')
            self.assert_var_units (root, 'Elevation', '-')

            self.assert_var_units (root, 'x', 'm')
        finally:
            root.close ()

class TestRectilinear (TestNc):
    nc_files = dict (
        test_0d='test-0d-00-rectilinear.nc',
        test_1d='test-1d-00-rectilinear.nc',
        test_2d='test-2d-00-rectilinear.nc',
        test_3d='test-3d-00-rectilinear.nc',
    )

    def test_1d (self):
        nc_file = self.nc_files['test_1d']

        field = RectilinearField ((1, 2, 4, 5), indexing='ij', units=('m', ))
        data = np.arange (4.)
        field.add_field ('Elevation', data, centering='point')

        attrs = dict (description='Example 1D nc file', author='Eric')
        field_tofile (field, nc_file, attrs=attrs, append=True)

        self.assertTrue (os.path.isfile (nc_file))

        try:
            root = self.open_nc_file (nc_file)
        except Exception:
            raise AssertionError ('%s: Could not open' % nc_file)
        else:
            self.assert_var_names (root, ['Elevation', 'x', 't', 'dummy'])
            self.assert_dimension_keys (root, ['n_points', 'n_cells', 'n_vertices', 'nx', 'nt'])
            self.assert_var_values (root, 'x', [1, 2, 4, 5])

            self.assert_var_name (root, 'Elevation', 'Elevation')
            self.assert_var_units (root, 'Elevation', '-')

            self.assert_var_units (root, 'x', 'm')
        finally:
            root.close ()

    def test_2d (self):
        nc_file = self.nc_files['test_2d']

        field = RectilinearField ((1, 4, 5), (2, 3),
                                  indexing='ij', units=('degrees_north', 'degrees_east'),
                                  coordinate_names=['latitude', 'longitude'])

        data = np.arange (6.)

        field.add_field ('Temperature', data*10, centering='point', units='C')
        field.add_field ('Elevation', data, centering='point', units='meters')
        field.add_field ('Velocity', data*100, centering='point', units='m/s')
        field.add_field ('Temp', data*2, centering='point', units='F')

        attrs = dict (description='Example nc file', author='Eric')
        field_tofile (field, nc_file, attrs=attrs, append=True)

        self.assertTrue (os.path.isfile (nc_file))

        try:
            root = self.open_nc_file (nc_file)
        except Exception:
            raise AssertionError ('%s: Could not open' % nc_file)
        else:
            self.assert_var_names (root, ['Temperature', 'Elevation',
                                          'Velocity', 'Temp',
                                          'x', 'y', 't', 'dummy'])
            self.assert_dimension_keys (root, ['n_points', 'n_cells', 'n_vertices', 'nx', 'ny', 'nt'])
            self.assert_var_values (root, 'x', [2., 3.])
            self.assert_var_values (root, 'y', [1., 4., 5.])
            self.assert_var_long_name (root, 'x', 'longitude')
            self.assert_var_long_name (root, 'y', 'latitude')
            self.assert_var_units (root, 'x', 'degrees_east')
            self.assert_var_units (root, 'y', 'degrees_north')

            for name in ['Temperature', 'Elevation', 'Velocity', 'Temp']:
                self.assert_var_name (root, name, name)
            for (v, u) in dict (Temperature='C', Elevation='meters',
                                Velocity='m/s', Temp='F').items ():
                self.assert_var_units (root, v, u)
        finally:
            root.close ()

class TestStructured (TestNc):
    nc_files = dict (
        test_0d='test-0d-00-structured.nc',
        test_1d='test-1d-00-structured.nc',
        test_2d='test-2d-00-structured.nc',
        test_3d='test-3d-00-structured.nc',
    )

    def test_1d (self):
        nc_file = self.nc_files['test_1d']

        field = StructuredField ((1, 2, 4, 5), (4, ), indexing='ij', units=('m', ))
        data = np.arange (4.)
        field.add_field ('Elevation', data, centering='point')

        attrs = dict (description='Example 1D nc file', author='Eric')
        field_tofile (field, nc_file, attrs=attrs, append=True)

        self.assertTrue (os.path.isfile (nc_file))

        try:
            root = self.open_nc_file (nc_file)
        except Exception:
            raise AssertionError ('%s: Could not open' % nc_file)
        else:
            self.assert_var_names (root, ['Elevation', 'x', 't', 'dummy'])
            self.assert_dimension_keys (root, ['n_points', 'n_cells', 'n_vertices', 'nx', 'nt'])
            self.assert_var_values (root, 'x', [1, 2, 4, 5])

            self.assert_var_name (root, 'Elevation', 'Elevation')
            self.assert_var_units (root, 'Elevation', '-')

            self.assert_var_units (root, 'x', 'm')
        finally:
            root.close ()

    def test_2d (self):
        nc_file = self.nc_files['test_2d']

        field = StructuredField ((1, 4, 5, 1, 4, 5), (2, 3, 2, 3, 2, 3), (3, 2),
                                 indexing='ij', units=('m', 'km'))

        data = np.arange (6.)

        field.add_field ('Temperature', data*10, centering='point', units='C')
        field.add_field ('Elevation', data, centering='point', units='meters')
        field.add_field ('Velocity', data*100, centering='point', units='m/s')
        field.add_field ('Temp', data*2, centering='point', units='F')

        attrs = dict (description='Example nc file', author='Eric')
        field_tofile (field, nc_file, attrs=attrs, append=True)

        self.assertTrue (os.path.isfile (nc_file))

        try:
            root = self.open_nc_file (nc_file)
        except Exception:
            raise AssertionError ('%s: Could not open' % nc_file)
        else:
            self.assert_var_names (root, ['Temperature', 'Elevation',
                                          'Velocity', 'Temp',
                                          'x', 'y', 't', 'dummy'])
            self.assert_dimension_keys (root, ['n_points', 'n_cells', 'n_vertices', 'nx', 'ny', 'nt'])
            self.assert_var_values (root, 'x', [2., 3.] * 3)
            self.assert_var_values (root, 'y', [1., 4., 5.] * 2)

            for name in ['Temperature', 'Elevation', 'Velocity', 'Temp']:
                self.assert_var_name (root, name, name)
            for (v, u) in dict (Temperature='C', Elevation='meters',
                                Velocity='m/s', Temp='F').items ():
                self.assert_var_units (root, v, u)
        finally:
            root.close ()

class TestUnstructured (TestNc):
    nc_files = dict (
        test_0d='test-0d-00.ncu',
        test_1d='test-1d-00.ncu',
        test_2d='test-2d-00.ncu',
        test_3d='test-3d-00.ncu',
    )

    def test_1d (self):
        nc_file = self.nc_files['test_1d']

        field = UnstructuredField ([0, 1, 4, 10], [0, 1, 1, 2, 2, 3],
                                   [2, 4, 6], units=('m', ))

        field.add_field ('point_field', np.arange (4), centering='point', units='C')
        field.add_field ('cell_field', np.arange (3)*10. , centering='zonal', units='F')

        field_tofile (field, nc_file, append=False)

    def test_2d (self):
        nc_file = self.nc_files['test_2d']

        field = UnstructuredField ([0, 2, 1, 3], [0, 0, 1, 1],
                                   [0, 2, 1, 2, 3, 1], [3, 6],
                                   units=('m', 'm'))

        data = np.arange (4)
        field.add_field ('point_field', data, centering='point', units='m')

        data = np.arange (2)
        field.add_field ('cell_field', data, centering='zonal',
                         units='m^2')

        field_tofile (field, nc_file, append=False)

        #with self.open_nc_file (nc_file) as root:
        try:
            root = self.open_nc_file (nc_file)
        except Exception:
            raise AssertionError ('%s: Could not open' % nc_file)
        else:
            self.assert_var_names (root, ['point_field', 'cell_field',
                                          'x', 'y', 't', 'connectivity',
                                          'offset', 'dummy'])
            self.assert_dimension_keys (root, ['n_cells', 'n_points',
                                               'n_vertices', 'nt'])
            self.assert_var_values (root, 'x', [0., 2., 1., 3.])
            self.assert_var_values (root, 'y', [0., 0., 1., 1.])
            self.assert_var_values (root, 'offset', [3, 6])
            self.assert_var_values (root, 'connectivity', [0, 2, 1, 2, 3, 1])

            self.assert_var_name (root, 'point_field', 'point_field')
            self.assert_var_name (root, 'cell_field', 'cell_field')
            self.assert_var_units (root, 'point_field', 'm')
            self.assert_var_units (root, 'cell_field', 'm^2')
        finally:
            root.close ()

if __name__ == '__main__':
    unittest.main ()

