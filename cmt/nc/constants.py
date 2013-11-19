#! /usr/bin/env python

_VALID_NETCDF_FORMATS = set([
    'NETCDF3_CLASSIC',
    'NETCDF3_64BIT',
])

_NP_TO_NC_TYPE = {
    'float32': 'f4',
    'float64': 'f8',
    'int8': 'i1',
    'int16': 'i2',
    'int32': 'i4',
    'int64': 'i8',
    'uint8': 'u1',
    'uint16': 'u2',
    'uint32': 'u4',
    'uint64': 'u8',
}

import os
from scipy.io import netcdf as nc3
try:
    import netCDF4 as nc4
except ImportError:
    warnings.warn('Unable to import netCDF4.', ImportWarning)
else:
    _VALID_NETCDF_FORMATS |= set(['NETCDF4_CLASSIC', 'NETCDF4'])


def assert_valid_netcdf_format(format):
    if format not in _VALID_NETCDF_FORMATS:
        raise ValueError('%s: format is one of %s' %
                         (format, ', '.join(_VALID_NETCDF_FORMATS)))


def open_netcdf(path, mode='r', format='NETCDF3_CLASSIC', append=False):
    assert_valid_netcdf_format(format)

    if mode != 'r':
        if os.path.isfile(path) and append:
            mode = 'a'
        else:
            mode = 'w'

    if format == 'NETCDF3_CLASSIC':
        root = nc3.netcdf_file(path, mode, version=1)
    elif format == 'NETCDF3_64BIT':
        root = nc3.netcdf_file(path, mode, version=2)
    else:
        root = nc4.Dataset(path, mode, format=format)

    return root
