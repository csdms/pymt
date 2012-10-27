#! /usr/bin/env python

import os
import unittest
import numpy as np

from cmt.grids import RasterField
from cmt.nc import field_tofile

class TestNC (unittest.TestCase):
    nc_files = dict (
        test_0d='test-0d-00.nc',
        test_1d='test-1d-00.nc',
        test_2d='test-1d-00.nc',
        test_3d='test-1d-00.nc',
    )

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

    def test_2d (self):
        nc_file = self.nc_files['test_2d']
        field = RasterField ((3,2), (2.,1), (0,0.5),
                             indexing='ij', units=('m', 'km'))

        data = np.arange (6.)

        field.add_field ('Temperature', data*10, centering='point', units='C')
        field.add_field ('Elevation', data, centering='point', units='meters')
        field.add_field ('Velocity', data*100, centering='point', units='m/s')
        field.add_field ('Temp', data*2, centering='point', units='F')

        try:
            os.remove (nc_file)
        except OSError:
            pass

        attrs = dict (description='Example nc file', author='Eric')
        field_tofile (field, nc_file, attrs=attrs, append=True)

        self.assertTrue (os.path.isfile (nc_file))

    def test_3d (self):
        nc_file = self.nc_files['test_3d']

        field = RasterField ((2, 3, 4), (1, 2, 3), (-1, 0, 1),
                             indexing='ij', units=('mm', 'm', 'km'))

        data = np.arange (24.)
        field.add_field ('Temperature', data*10, centering='point', units='C')
        field.add_field ('Elevation', data, centering='point', units='meters')
        field.add_field ('Velocity', data*100, centering='point', units='m/s')
        field.add_field ('Temp', data*2, centering='point', units='F')

        try:
            os.remove (nc_file)
        except OSError:
            pass

        attrs = dict (description='Example 3D nc file', author='Eric')
        field_tofile (field, nc_file, attrs=attrs, append=True)

        self.assertTrue (os.path.isfile (nc_file))

    def test_1d (self):
        nc_file = self.nc_files['test_1d']
        field = RasterField ((12, ), (1, ), (-1, ), indexing='ij', units=('m', ))
        data = np.arange (12.)
        field.add_field ('Elevation', data, centering='point')

        try:
            os.remove (nc_file)
        except OSError:
            pass

        attrs = dict (description='Example 1D nc file', author='Eric')
        field_tofile (field, nc_file, attrs=attrs, append=True)

        self.assertTrue (os.path.isfile (nc_file))

    def test_0d (self):
        nc_file = self.nc_files['test_0d']
        field = RasterField ((1, ), (0, ), (0, ), indexing='ij', units=('m', ))

        try:
            os.remove (nc_file)
        except OSError:
            pass

        attrs = dict (description='Example 0D nc file', author='Eric')
        for i in range (10):
            field.add_field ('Elevation', i, centering='point')
            field_tofile (field, nc_file, attrs=attrs, append=True)

        self.assertTrue (os.path.isfile (nc_file))

if __name__ == '__main__':
    unittest.main ()

