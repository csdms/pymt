#! /usr/bin/env python

import os
import numpy as np
from numpy.testing import assert_array_equal
from nose.tools import (assert_true, assert_equal, assert_items_equal,
                        assert_tuple_equal)

from cmt.grids import RasterField
from cmt.printers.nc.database import Database


_TMP_DIR = 'tmp'


def setup():
    import tempfile

    globals().update({
        '_TMP_DIR': tempfile.mkdtemp(dir='.')
    })


def teardown():
    from shutil import rmtree

    rmtree(_TMP_DIR)


def open_nc_file(filename):
    import netCDF4 as nc
    return nc.Dataset(filename, 'r', format='NETCDF4')


def test_2d_constant_shape():
    #Create field and add some data to it that we will write to a
    # NetCDF file database.

    #nc_file = 'Elevation_time_series_0000.nc'
    nc_file = os.path.join(_TMP_DIR, '2d_elevation_time_series.nc')

    data = np.arange(6.)

    field = RasterField((2, 3), (1.,1.), (0.,0.), indexing='ij')
    field.add_field('Elevation', data, centering='point')

    #Create database of 'Elevation' values. Data are written to the
    # NetCDF file Elevation_time_series.nc.

    db = Database()
    db.open(nc_file, 'Elevation')
    db.write(field)

    assert_true(os.path.isfile(nc_file))

    # Append data to the NetCDF file.
    data *= 2.
    db.write(field)

    db.close()

    try:
        root = open_nc_file(nc_file)
    except Exception:
        raise AssertionError('%s: Could not open' % nc_file)
    else:
        assert_items_equal(['x', 'y', 'time'], root.dimensions.keys())
        assert_items_equal(['Elevation', 'x', 'y', 'time',
                            'mesh'], root.variables)

        assert_equal(3, len(root.dimensions['x']))
        assert_equal(2, len(root.dimensions['y']))
        assert_equal(2, len(root.dimensions['time']))

        assert_tuple_equal((2, 2, 3), root.variables['Elevation'].shape)

        assert_array_equal(np.arange(6.).reshape(2, 3),
                           root.variables['Elevation'][0])
        assert_array_equal(np.arange(6.).reshape((2, 3)) * 2.,
                           root.variables['Elevation'][1])

        assert_array_equal([0., 1.], root.variables['y'])
        assert_array_equal([0., 1., 2.], root.variables['x'])

        assert_equal('Elevation', root.variables['Elevation'].long_name)
        assert_equal('-', root.variables['Elevation'].units)

        root.close()


def test_2d_changing_shape():
    #Create field and add some data to it that we will write to a
    # NetCDF file database.

    nc_file = os.path.join(_TMP_DIR, 'Temperature_time_series.nc')

    data = np.arange(6.)

    field = RasterField((3,2), (1.,1.), (0.,0.))
    field.add_field('Temperature', data, centering='point')

    db = Database()
    db.open(nc_file, 'Temperature')
    db.write(field)

    assert_true(os.path.isfile(nc_file))

    # Create a new field and write the data to the database. Since
    # the size of the field has changed, the data will be written
    # to a new file, Elevation_time_series_0000.nc.

    field = RasterField((3,3), (1.,1.), (0.,0.))
    data = np.arange(9.)
    field.add_field('Temperature', data, centering='point')

    db.write(field)
    assert_true(os.path.isfile(os.path.join(_TMP_DIR,
                                            'Temperature_time_series_0000.nc')))

    db.close()

    try:
        nc_file = os.path.join(_TMP_DIR,
                               'Temperature_time_series_0000.nc')
        root = open_nc_file(nc_file)
    except Exception:
        raise AssertionError('%s: Could not open' % nc_file)
    else:
        assert_items_equal(['x', 'y', 'time'], root.dimensions.keys())
        assert_items_equal(['Temperature', 'x', 'y', 'time',
                            'mesh'], root.variables)

        assert_equal(3, len(root.dimensions['x']))
        assert_equal(3, len(root.dimensions['y']))
        assert_equal(1, len(root.dimensions['time']))

        assert_tuple_equal((1, 3, 3), root.variables['Temperature'].shape)

        assert_array_equal(np.arange(9.).reshape((3, 3)),
                           root.variables['Temperature'][0])

        assert_array_equal([0., 1., 2.], root.variables['x'])
        assert_array_equal([0., 1., 2.], root.variables['y'])

        assert_equal('Temperature', root.variables['Temperature'].long_name)
        assert_equal('-', root.variables['Temperature'].units)

        root.close()
