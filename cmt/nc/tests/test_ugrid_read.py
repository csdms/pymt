import unittest
import os

from cmt.nc.read import field_fromfile


class DataTestFileMixIn(object):
    def data_file(self, name):
        return os.path.join(self.data_dir(), name)

    def data_dir(self):
        return os.path.join(os.path.dirname(__file__), 'data')


class TestNetcdfRead(unittest.TestCase, DataTestFileMixIn):
    def test_unstructured_2d(self):
        field = field_fromfile(self.data_file('unstructured.2d.nc'),
                               format='NETCDF4')

    def test_rectilinear_1d(self):
        field = field_fromfile(self.data_file('rectilinear.1d.nc'),
                               format='NETCDF4')

    def test_rectilinear_2d(self):
        field = field_fromfile(self.data_file('rectilinear.2d.nc'),
                               format='NETCDF4')

    def test_rectilinear_3d(self):
        field = field_fromfile(self.data_file('rectilinear.3d.nc'),
                               format='NETCDF4')
