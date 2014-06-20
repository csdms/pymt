import unittest
import os
import urllib2

from cmt.printers.nc.read import field_fromfile


def fetch_data_file(filename):
    url = ('http://csdms.colorado.edu/thredds/fileServer/benchmark/ugrid/' +
           filename)
    remote_file = urllib2.urlopen(url)
    with open(filename, 'w') as netcdf_file:
        netcdf_file.write(remote_file.read())

    return os.path.abspath(filename)


class DataTestFileMixIn(object):
    def data_file(self, name):
        return os.path.join(self.data_dir(), name)

    def data_dir(self):
        return os.path.join(os.path.dirname(__file__), 'data')


class TestNetcdfRead(unittest.TestCase, DataTestFileMixIn):
    def test_unstructured_2d(self):
        field = field_fromfile(fetch_data_file('unstructured.2d.nc'),
                               format='NETCDF4')

    def test_rectilinear_1d(self):
        field = field_fromfile(fetch_data_file('rectilinear.1d.nc'),
                               format='NETCDF4')

    def test_rectilinear_2d(self):
        field = field_fromfile(fetch_data_file('rectilinear.2d.nc'),
                               format='NETCDF4')

    def test_rectilinear_3d(self):
        field = field_fromfile(fetch_data_file('rectilinear.3d.nc'),
                               format='NETCDF4')
