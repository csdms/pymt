import numpy as np

from cmt.grids import (RasterField, RectilinearField, StructuredField)
from cmt.printers.nc.ugrid import (NetcdfRectilinearField,
                                   NetcdfStructuredField,
                                   NetcdfUnstructuredField)

_TMP_DIR = 'tmp'
_TMP_FILES = []


def setup():
    import tempfile

    globals().update({
        '_TMP_DIR': tempfile.mkdtemp(dir='.'),
        '_TMP_FILES': [],
    })


def teardown():
    from shutil import rmtree

    rmtree(_TMP_DIR)


def unique_name(**kwds):
    import tempfile
    import os

    kwds.setdefault('dir', os.getcwd())

    (handle, name) = tempfile.mkstemp(**kwds)
    os.close(handle)
    _TMP_FILES.append(name)
    return name


def open_unique(**kwds):
    import netCDF4 as nc4
    import tempfile
    (handle, name) = tempfile.mkstemp(**kwds)
    handle.close()

    root = nc4.Dataset(name, 'w', format='NETCDF4')
    _TMP_FILES.append(name)
    return root


def new_raster(**kwds):
    ndims = kwds.pop('ndims', 1)
    shape = np.random.random_integers(2, 101, ndims)
    spacing = (1. - np.random.random(ndims)) * 100.
    origin = (np.random.random(ndims) - .5) * 100.

    return RasterField(shape, spacing, origin, **kwds)


def new_rectilinear(**kwds):
    ndims = kwds.pop('ndims', 1)
    shape = np.random.random_integers(2, 101, ndims)
    args = []
    for size in shape:
        args.append(np.cumsum((1. - np.random.random(size))))

    return RectilinearField(*args, **kwds)


def new_structured(**kwds):
    ndims = kwds.pop('ndims', 1)
    shape = np.random.random_integers(2, 101, ndims)

    coords = []
    for size in shape:
        coords.append(np.cumsum((1. - np.random.random(size))))

    if len(coords) > 1:
        args = np.meshgrid(*coords, indexing='ij')
    else:
        args = coords
    args.append(shape)

    return StructuredField(*args, **kwds)


def test_rectilinear_1d_points():
    field = new_rectilinear()
    data = np.arange(field.get_point_count())
    field.add_field('air_temperature', data, centering='point', units='F')

    _ = NetcdfRectilinearField(
        unique_name(prefix='rectilinear.1d.', suffix='.nc'), field)


def test_rectilinear_2d_points():
    field = new_rectilinear(ndims=2)
    data = np.arange(field.get_point_count(), dtype=np.float64)
    field.add_field('air__temperature', data, centering='point', units='F')

    _ = NetcdfRectilinearField(
        unique_name(prefix='rectilinear.2d.', suffix='.nc'), field)


def test_rectilinear_3d_points():
    field = new_rectilinear(
        ndims=3,
        coordinate_names=('elevation', 'latitude', 'longitude'),
        units=('m', 'degrees_north', 'degrees_east'))
    data = np.arange(field.get_point_count(), dtype=np.float64)
    field.add_field('air__temperature', data, centering='point', units='F')

    _ = NetcdfRectilinearField(
        unique_name(prefix='rectilinear.3d.', suffix='.nc'), field)


def test_structured_1d_points():
    field = new_rectilinear()
    data = np.arange(field.get_point_count())
    field.add_field('air_temperature', data, centering='point', units='F')

    _ = NetcdfStructuredField(
        unique_name(prefix='structured.1d.', suffix='.nc'), field)


def test_structured_2d_points():
    field = new_rectilinear(ndims=2)
    data = np.arange(field.get_point_count(), dtype=np.float64)
    field.add_field('air__temperature', data, centering='point', units='F')

    _ = NetcdfStructuredField(
        unique_name(prefix='structured.2d.', suffix='.nc'), field)


def test_structured_3d_points():
    field = new_rectilinear(
        ndims=3,
        coordinate_names=('elevation', 'latitude', 'longitude'),
        units=('m', 'degrees_north', 'degrees_east'))
    data = np.arange(field.get_point_count(), dtype=np.float64)
    field.add_field('air__temperature', data, centering='point', units='F')

    _ = NetcdfStructuredField(
        unique_name(prefix='structured.3d.', suffix='.nc'), field)


def test_unstructured_1d_points():
    field = new_rectilinear()
    data = np.arange(field.get_point_count())
    field.add_field('air_temperature', data, centering='point', units='F')

    _ = NetcdfUnstructuredField(
        unique_name(prefix='unstructured.1d.', suffix='.nc'), field)


def test_unstructured_2d_points():
    field = new_rectilinear(ndims=2)
    data = np.arange(field.get_point_count(), dtype=np.float64)
    field.add_field('air__temperature', data, centering='point', units='F')

    _ = NetcdfUnstructuredField(
        unique_name(prefix='unstructured.2d.', suffix='.nc'), field)


def test_unstructured_3d_points():
    field = new_rectilinear(
        ndims=3,
        coordinate_names=('elevation', 'latitude', 'longitude'),
        units=('m', 'degrees_north', 'degrees_east'))
    data = np.arange(field.get_point_count(), dtype=np.float64)
    field.add_field('air__temperature', data, centering='point', units='F')

    _ = NetcdfUnstructuredField(
        unique_name(prefix='unstructured.3d.', suffix='.nc'), field)
