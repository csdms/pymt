#! /usr/bin/env python

import os
import unittest
import numpy as np

from cmt.grids import RasterField
from cmt.nc import Database

class TestNcDatabase (unittest.TestCase):
    nc_files = [
        'Elevation_time_series.nc',
        'Temperature_time_series.nc',
        'Temperature_time_series_0000.nc',
    ]

    def setUp (self):
        for file in self.nc_files:
            try:
                os.remove (file)
            except OSError:
                pass

    def tearDown (self):
        for file in self.nc_files:
            try:
                os.remove (file)
            except OSError:
                pass

    def test_2d_constant_shape (self):
        #Create field and add some data to it that we will write to a
        # NetCDF file database.

        nc_file = 'Elevation_time_series.nc'

        data = np.arange (6.)

        field = RasterField ((3,2), (1.,1.), (0.,0.))
        field.add_field ('Elevation', data, centering='point')

        #Create database of 'Elevation' values. Data are written to the
        # NetCDF file Elevation_time_series.nc.

        db = Database ()
        db.open (nc_file, 'Elevation')
        db.write (field)

        self.assertTrue (os.path.isfile (nc_file))

        # Append data to the NetCDF file.
        data *= 2.
        db.write (field)

        db.close ()

        with self.open_nc_file (nc_file) as root:
            self.assert_dimension_keys (root, ['nx', 'ny', 'nt'])
            self.assert_var_names (root, ['Elevation', 'x', 'y', 't', 'dummy'])

            self.assert_dimension_size (root, 'nx', 3)
            self.assert_dimension_size (root, 'ny', 2)
            self.assert_dimension_size (root, 'nt', 2)

            self.assert_var_shape (root, 'Elevation', (2, 2, 3))

            self.assert_var_values_at_time (root, 'Elevation', 0, np.arange (6.))
            self.assert_var_values_at_time (root, 'Elevation', 1, np.arange (6.) * 2.)

            self.assert_var_values (root, 'x', [0., 1., 2.])
            self.assert_var_values (root, 'y', [0., 1.])
            self.assert_var_name (root, 'Elevation', 'Elevation')
            self.assert_var_units (root, 'Elevation', '-')

    def test_2d_changing_shape (self):
        #Create field and add some data to it that we will write to a
        # NetCDF file database.

        nc_file = 'Temperature_time_series.nc'

        data = np.arange (6.)

        field = RasterField ((3,2), (1.,1.), (0.,0.))
        field.add_field ('Temperature', data, centering='point')

        db = Database ()
        db.open (nc_file, 'Temperature')
        db.write (field)

        self.assertTrue (os.path.isfile (nc_file))

        # Create a new field and write the data to the database. Since
        # the size of the field has changed, the data will be written
        # to a new file, Elevation_time_series_0000.nc.

        field = RasterField ((3,3), (1.,1.), (0.,0.))
        data = np.arange (9.)
        field.add_field ('Temperature', data, centering='point')

        db.write (field)
        self.assertTrue (os.path.isfile ('./Temperature_time_series_0000.nc'))

        db.close ()

        with self.open_nc_file ('Temperature_time_series_0000.nc') as root:
            self.assert_dimension_keys (root, ['nx', 'ny', 'nt'])
            self.assert_var_names (root, ['Temperature', 'x', 'y', 't', 'dummy'])

            self.assert_dimension_size (root, 'nx', 3)
            self.assert_dimension_size (root, 'ny', 3)
            self.assert_dimension_size (root, 'nt', 1)

            self.assert_var_shape (root, 'Temperature', (1, 3, 3))

            self.assert_var_values_at_time (root, 'Temperature', 0, np.arange (9.))

            self.assert_var_values (root, 'x', [0., 1., 2.])
            self.assert_var_values (root, 'y', [0., 1., 2.])
            self.assert_var_name (root, 'Temperature', 'Temperature')
            self.assert_var_units (root, 'Temperature', '-')

    def assert_dimension_size (self, root, dimension, expected_size):
        size = len (root.dimensions[dimension])
        self.assertEqual (size, expected_size)
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
    def assert_var_shape (self, root, var, expected_shape):
        vars = root.variables
        values = vars[var][:]
        self.assertTupleEqual (values.shape, tuple (expected_shape))
    def assert_var_values_at_time (self, root, var, i, expected_values):
        vars = root.variables
        values = vars[var][:]
        self.assertListEqual (list (values[i,:,:].flatten ()), list (expected_values))
    def assert_var_name (self, root, var, expected_name):
        vars = root.variables
        name = vars[var].long_name
        self.assertEqual (name, expected_name)
    def assert_var_units (self, root, var, expected_units):
        vars = root.variables
        units = vars[var].units
        self.assertEqual (units, expected_units)

    @staticmethod
    def open_nc_file (file):
        import netCDF4 as nc
        return nc.Dataset (file, 'r', format='NETCDF4')

if __name__ == '__main__':
    unittest.main ()

