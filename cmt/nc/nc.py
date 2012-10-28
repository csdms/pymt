#! /usr/bin/env python

"""
Examples
========

>>> from cmt.grids import RasterField
>>> import numpy as np
>>> f = RasterField ((3,2), (2.,1), (0,0.5), indexing='ij', units=('m', 'km'))
>>> data = np.arange (6.)
>>> f.add_field ('Temperature', data*10, centering='point', units='C')
>>> f.add_field ('Elevation', data, centering='point', units='meters')
>>> f.add_field ('Velocity', data*100, centering='point', units='m/s')
>>> f.add_field ('Temp', data*2, centering='point', units='F')
>>> f.get_coordinate_units (0)
'm'
>>> f.get_coordinate_units (1)
'km'

>>> attrs = dict (description='Example nc file', author='Eric')
>>> field_tofile (f, 'test00.nc', attrs=attrs, append=True)

>>> f = RasterField ((6,1), (1,1), (0,0), indexing='ij')
>>> data = np.arange (6.)
>>> f.add_field ('Elevation', data, centering='point')
>>> f.add_field ('Temperature', data*10, centering='point')




>>> f = RasterField ((2, 3, 4), (1, 2, 3), (-1, 0, 1), indexing='ij', units=('mm', 'm', 'km'))
>>> data = np.arange (24.)
>>> f.add_field ('Temperature', data*10, centering='point', units='C')
>>> f.add_field ('Elevation', data, centering='point', units='meters')
>>> f.add_field ('Velocity', data*100, centering='point', units='m/s')
>>> f.add_field ('Temp', data*2, centering='point', units='F')
>>> f.get_coordinate_units (0) == f.get_z_units (), f.get_z_units ()
(True, 'mm')
>>> f.get_coordinate_units (1) == f.get_y_units (), f.get_y_units ()
(True, 'm')
>>> f.get_coordinate_units (2) == f.get_x_units (), f.get_x_units ()
(True, 'km')

>>> attrs = dict (description='Example 3D nc file', author='Eric')
>>> field_tofile (f, 'test-3d-00.nc', attrs=attrs, append=True)



>>> f = RasterField ((12, ), (1, ), (-1, ), indexing='ij', units=('m', ))
>>> data = np.arange (12.)
>>> f.add_field ('Elevation', data, centering='point')

>>> attrs = dict (description='Example 1D nc file', author='Eric')
>>> field_tofile (f, 'test-1d-00.nc', attrs=attrs, append=True)



>>> f = RasterField ((1, ), (0, ), (0, ), indexing='ij', units=('m', ))

>>> attrs = dict (description='Example 0D nc file', author='Eric')
>>> for i in range (10):
...     f.add_field ('Elevation', i, centering='point')
...     field_tofile (f, 'test-0d-00.nc', attrs=attrs, append=True)



"""

import os
import string

import numpy as np

from cmt.grids import RectilinearField
from cmt.grids import NonStructuredGridError, NonUniformGridError
from cmt.verbose import CMTLogger

logger = CMTLogger ('NetCDF', 20)

class Error (Exception):
    pass
class DimensionError (Error):
    def __init__ (self, dim0, dim1):
        self._dim0 = 'x'.join ([str (d) for d in dim0])
        self._dim1 = 'x'.join ([str (d) for d in dim1])
    def __str__ (self):
        return '%s: Dimension mismatch (should be %s)' % (self._dim1, self._dim0)
class RankError(Error):
    def __init__ (self, rank):
        self._rank = rank
    def __str__ (self):
        return '%d: Grid rank must be <= 3' % self._rank

def remove_singleton (array, shape):
    try:
        assert (array.size == shape.size)
    except AttributeError:
        return remove_singleton (np.array (array), np.array (shape))
    else:
        return array[shape>1]
try:
    import csdms_utils
except ImportError:
    print 'Unable to import csdms_utils'

class NetcdfWriter (object):
    valid_keywords = set (['dtype', 'var_units', 'time_units', 'time_long_name',
                           'time_reference', 'comment', 'long_var_name'])
    """Base class for NetCDF writers.

    The subclass is responsible for opening the NetCDF file and setting
    the *_nc_file* member.

    """
    def _check_keywords (self, **kwargs):
        keywords = set (kwargs.keys ())
        if not keywords.issubset (self.valid_keywords):
            invalid = keywords - valid_keywords
            raise TypeError (
                '%s is an invalid keyword argument for this function' %
                ','.join (invalid))

    def __init__ (self, shape, spacing, **kwargs):
        try:
            self._check_keywords (**kwargs)
        except TypeError:
            raise

        self._shape = shape
        self._spacing = spacing

        self._attrs = dict (dtype='float64',
                            var_units='-',
                            time_units='-',
                            time_long_name='Simulation time',
                            time_reference='1973-3-14 0:0:0',
                            comment='Created with cmt.nc.NetcdfWriter')

        self._attrs.update (**kwargs)

    def open (self, path, var_name, **kwargs):
        try:
            self._check_keywords (**kwargs)
        except TypeError:
            raise

        if not self._attrs.has_key ('long_var_name'):
            self._attrs['long_var_name'] = var_name

        self._var_name = var_name
        self._attrs.update (**kwargs)

    def close (self):
        try:
            self._nc_file.close_file ()
        except AttributeError:
            # The NetCDF file was never opened. Silently ignore.
            pass
    def write (self, array):
        try:
            array.shape = self._shape
        except AttributeError:
            raise TypeError ('array must be type ndarray not %s', type (array))
        except ValueError:
            raise DimensionError (self._shape, array.shape)

class NcpsWriter (NetcdfWriter):
    def __init__ (self, *args, **kwargs):
        super (NcpsWriter, self).__init__ (*args, **kwargs)
        self._nc_file = csdms_utils.ncps_files.ncps_file ()
        self._time = 0.

    def open (self, path, var_name, **kwargs):
        super (NcpsWriter, self).open (path, var_name, **kwargs)
        ok = self._nc_file.open_new_file (path,
                                          profile_length=self._shape[0],
                                          var_names=[var_name],
                                          long_names=[self._attrs['long_var_name']],
                                          units_names=[self._attrs['var_units']],
                                          dtypes=[self._attrs['dtype']],
                                          time_units=self._attrs['time_units'])
    def write (self, array):
        super (NcpsWriter, self).write (array)
        self._nc_file.add_profile (array, self._var_name, self._time)
        self._time += 1

class NcgsWriter (NetcdfWriter):
    def __init__ (self, *args, **kwargs):
        super (NcgsWriter, self).__init__ (*args, **kwargs)
        self._nc_file = csdms_utils.ncgs_files.ncgs_file ()

    def open (self, path, var_name, **kwargs):
        super (NcgsWriter, self).open (path, var_name, **kwargs)
        info = csdms_utils.rti_files.make_info (path, self._shape[1],
                                                self._shape[0],
                                                self._spacing[1], 
                                                self._spacing[0])
        ok = self._nc_file.open_new_file (path, info, var_name=var_name,
                                          units_name=self._attrs['var_units'],
                                          dtype=self._attrs['dtype'])
    def write (self, array):
        super (NcgsWriter, self).write (array)
        self._nc_file.add_grid (array, self._var_name)


class NccsWriter (NetcdfWriter):
    def __init__ (self, *args, **kwargs):
        super (NccsWriter, self).__init__ (*args, **kwargs)
        self._nc_file = csdms_utils.nccs_files.nccs_file ()

    def open (self, path, var_name, **kwargs):
        super (NccsWriter, self).open (path, var_name, **kwargs)
        ok = self._nc_file.open_new_file (path, shape=self._shape,
                                          res=self._spacing,
                                          dtype=self._attrs['dtype'],
                                          var_name=var_name,
                                          long_name=self._attrs['long_var_name'],
                                          units_name=self._attrs['var_units'],
                                          time_units=self._attrs['time_units'],
                                          time_long_name=self._attrs['time_long_name'],
                                          time_reference=self._attrs['time_reference'],
                                          comment=self._attrs['comment'])
    def write (self, array):
        super (NccsWriter, self).write (array)
        self._nc_file.add_cube (array, self._var_name)

def writer_from_shape (shape):
    if len (shape)==1:
        return NcpsWriter
    elif len (shape)==2:
        return NcgsWriter
    elif len (shape)==3:
        return NccsWriter
    raise RankError (len (shape))

def tofile (field, path, units={}):
    spacing = remove_singleton (field.get_spacing (), field.get_shape ())
    shape = remove_singleton (field.get_shape (), field.get_shape ())

    writer = writer_from_shape (shape)

    (root, ext) = os.path.splitext (path)
    file_name = string.Template (root + '_${var_name}' + ext)

    fields = field.get_point_fields ()
    for (var_name, array) in fields.items ():
        units_name = units.get (var_name, '-')
        nc_file = writer (shape, spacing)
        try:
            path = file_name.substitute (var_name=var_name)
            nc_file.open (path, var_name, var_units=units_name)
        except Exception as e:
            logger.warning ("ncgs: %s: Unable to open: %s" % (path, e))
        else:
            nc_file.write (array)
        finally:
            try:
                nc_file.close ()
            except AttributeError:
                logger.warning ('Unable to close')

def field_tofile (field, path, append=False, attrs={}, time=None,
                  time_units='days', time_reference='00:00:00 UTC'):
    """
Define a field that consists of two trianges that share two points.

::

       (2) - (3)
      /   \  /
    (0) - (1)


    >>> from cmt.grids import UnstructuredField
    >>> field = UnstructuredField ([0, 2, 1, 3], [0, 0, 1, 1], [0, 2, 1, 2, 3, 1], [3, 6], units=('m', 'm'))

Put some data at the points.

    >>> data = np.arange (4)
    >>> field.add_field ('point_field', data, centering='point', units='m')

Put some data at the cells.

    >>> data = np.arange (2)
    >>> field.add_field ('cell_field', data, centering='zonal', units='m^2')

Write the NetCDF file.

    >>> field_tofile (field, 'unstructured_grid_test.nc', append=False)

Check the values from the file.

    >>> import netCDF4 as nc
    >>> root = nc.Dataset ('unstructured_grid_test.nc', 'r', format='NETCDF4')
    >>> dims = root.dimensions.keys ()
    >>> dims.sort ()
    >>> print ', '.join (dims)
    n_cells, n_points, n_vertices, nt

    >>> vars = root.variables
    >>> print vars['x'][:]
    [ 0. 2. 1. 3.]
    >>> print vars['y'][:]
    [ 0. 0. 1. 1.]

    >>> print vars['point_field'].long_name
    point_field
    >>> print vars['point_field'].units
    m

    >>> print vars['cell_field'].long_name
    cell_field
    >>> print vars['cell_field'].units
    m^2
    """
    import netCDF4 as nc

    if os.path.isfile (path) and append:
        mode = 'a'
    else:
        mode = 'w'
    root = nc.Dataset (path, mode, format='NETCDF4')

    set_attributes (attrs, root)
    set_dimensions (field, root)
    set_variables (field, root, time=time, time_units=time_units,
                   time_reference=time_reference)

def set_attributes (attrs, root):
    for (key, val) in attrs.items ():
        setattr (root, key, val)

dimension_name = ['nz', 'ny', 'nx']

def set_dimensions (field, root):
    try:
        _set_structured_dimensions (field, root)
    except (NonStructuredGridError, NonUniformGridError):
        _set_unstructured_dimensions (field, root)

def _set_structured_dimensions (field, root):
    # Define dimensions

    try:
        shape = remove_singleton (field.get_shape (), field.get_shape ())
    except (NonStructuredGridError, NonUniformGridError):
        raise

    names = dimension_name[-len (shape):]

    dims = root.dimensions
    for (name, dimen) in zip (names, shape):
        if not name in dims:
            root.createDimension (name, dimen)

    if not 'nt' in dims:
        nt = root.createDimension ('nt', None)

def _set_unstructured_dimensions (field, root):
    dimensions = dict (n_points = field.get_point_count (),
                       n_cells = field.get_cell_count (),
                       n_vertices = field.get_vertex_count ())

    dims = root.dimensions
    for (name, dimen) in dimensions.items ():
        if not name in dims:
            root.createDimension (name, dimen)
    if not 'nt' in dims:
        nt = root.createDimension ('nt', None)

variable_name = ['z', 'y', 'x']
np_to_nc_type = {
    'float32': 'f4',
    'float64': 'f8',
    'int8': 'i1',
    'int16': 'i2',
    'int32': 'i4',
    'int64': 'i8',
    'uint8': 'u1',
    'uint16': 'u2',
    'uint32': 'u4',
    'uint64': 'u8'}

def set_variables (field, root, **kwds):
    try:
        _set_structured_variables (field, root, **kwds)
    except (NonStructuredGridError, NonUniformGridError):
        _set_unstructured_variables (field, root, **kwds)

def _set_structured_variables (field, root, time=None, time_units='days',
                               time_reference='00:00:00 UTC'):
    # Define and assign variables

    try:
        shape = remove_singleton (field.get_shape (), field.get_shape ())
    except (NonStructuredGridError, NonUniformGridError):
        raise

    spacing = remove_singleton (field.get_spacing (), field.get_shape ())
    origin = remove_singleton (field.get_origin (), field.get_shape ())

    if len (shape) > 0:
        dim_names = dimension_name[-len (shape):]
        var_names = variable_name[-len (shape):]
    else:
        dim_names = []
        var_names = []

    vars = root.variables

    try:
        t = vars['t']
    except KeyError:
        t = root.createVariable ('t', 'f8', ('nt', ))
        t.units = ' '.join ([time_units, 'since', time_reference])
        t.long_name = 'time'
    n_times = len (t)
    if time is not None:
        t[n_times] = time
    else:
        t[n_times] = n_times

    for (i, var_name) in enumerate (var_names):
        try:
            var = vars[var_name]
        except KeyError:
            var = root.createVariable (var_name, 'f8', (dim_names[i], ))
        var[:] = np.arange (shape[i]) * spacing[i] + origin[i]
        var.units = field.get_coordinate_units (i)
        var.long_name = var_name

    fields = field.get_point_fields ()
    for (var_name, array) in fields.items ():
        try:
            var = vars[var_name]
        except KeyError:
            var = root.createVariable (var_name,
                                       np_to_nc_type[str (array.dtype)],
                                       ['nt'] + dim_names)
        if array.size > 1:
            var[n_times,:] = array.flat
        else:
            var[n_times] = array[0]
        var.units = field.get_field_units (var_name)
        var.long_name = var_name

    try:
        var = vars['dummy']
    except KeyError:
        var = root.createVariable ('dummy', 'f8', ())
    var[0] = 0.
    var.units = '-'
    var.long_name = 'dummy'

def _set_unstructured_variables (field, root, time=None, time_units='days',
                                 time_reference='00:00:00 UTC'):
    vars = root.variables
    try:
        t = vars['t']
    except KeyError:
        t = root.createVariable ('t', 'f8', ('nt', ))
        t.units = ' '.join ([time_units, 'since', time_reference])
        t.long_name = 'time'
    n_times = len (t)
    if time is not None:
        t[n_times] = time
    else:
        t[n_times] = n_times

    try:
        x = vars['x']
    except KeyError:
        x = root.createVariable ('x', 'f8', ('n_points', ))
        x[:] = field.get_x ()
        x.units = field.get_x_units ()
        x.long_name = 'distance_in_x_dimension'
    try:
        y = vars['y']
    except KeyError:
        y = root.createVariable ('y', 'f8', ('n_points', ))
        y[:] = field.get_y ()
        y.units = field.get_y_units ()
        y.long_name = 'distance_in_y_dimension'

    try:
        c = vars['connectivity']
    except KeyError:
        c = root.createVariable ('connectivity', 'i8', ('n_vertices', ))
        c[:] = field.get_connectivity ()

    try:
        o = vars['offset']
    except KeyError:
        o = root.createVariable ('offset', 'i8', ('n_cells', ))
        o[:] = field.get_offset ()

    fields = field.get_point_fields ()
    for (var_name, array) in fields.items ():
        try:
            var = vars[var_name]
        except KeyError:
            var = root.createVariable (var_name,
                                       np_to_nc_type[str (array.dtype)],
                                       ('nt', 'n_points'))
        var[n_times,:] = array.flat
        var.units = field.get_field_units (var_name)
        var.long_name = var_name

    fields = field.get_cell_fields ()
    for (var_name, array) in fields.items ():
        try:
            var = vars[var_name]
        except KeyError:
            var = root.createVariable (var_name,
                                       np_to_nc_type[str (array.dtype)],
                                       ('nt', 'n_cells'))
        var[n_times,:] = array.flat
        var.units = field.get_field_units (var_name)
        var.long_name = var_name

    try:
        var = vars['dummy']
    except KeyError:
        var = root.createVariable ('dummy', 'f8', ())

    var[0] = 0.
    var.units = '-'
    var.long_name = 'dummy'

def field_to_nc (field, root):
    shape = field.get_shape ()

    # Define dimensions
    dims = root.dimensions.keys ()
    if not 'nx' in dims:
        nx = root.createDimension ('nx', shape[1])
    if not 'ny' in dims:
        ny = root.createDimension ('ny', shape[0])
    if not 'nt' in dims:
        nt = root.createDimension ('nt', None)

    # Define and assign variables
    vars = root.variables
    try:
        x = vars['x']
    except KeyError:
        x = root.createVariable ('x', 'f8', ('nx', ))
        x[:] = np.arange (shape[1])
    try:
        y = vars['y']
    except KeyError:
        y = root.createVariable ('y', 'f8', ('ny', ))
        y[:] = np.arange (shape[0])
    try:
        t = vars['t']
    except KeyError:
        t = root.createVariable ('t', 'f8', ('nt', ))
    n_times = len (t)
    t[n_times] = n_times

    fields = field.get_point_fields ()
    for (var_name, array) in fields.items ():
        try:
            var = vars[var_name]
        except KeyError:
            var = root.createVariable (var_name, 'f8', ('nt', 'nx', 'ny'))
        var[n_times,:,:] = array

def fromfile (file, allow_singleton=True):
    """
    >>> file_url = 'http://csdms.colorado.edu/thredds/dodsC/benchmark/sample/ramp_bathymetry.nc'
    >>> fields = fromfile (file_url)

    >>> print len (fields)
    1
    >>> print fields[0][0]
    0.0

    >>> field = fields[0][1]

    >>> x = field.get_x_coordinates ()
    >>> len (x) == 42
    True

    >>> y = field.get_y_coordinates ()
    >>> len (y) == 82
    True

    >>> all (x == np.arange (42)*500.-500.)
    True
    >>> all (y == np.arange (82)*500.-500.)
    True

    >>> print field.get_x_units ()
    m
    >>> print field.get_y_units ()
    m

    >>> names = field.keys ()
    >>> names.sort ()
    >>> print ','.join (names)
    Basement

    >>> units = [field.get_field_units (f) for f in names]
    >>> print ','.join (units)
    m

    """
    import netCDF4 as nc
    root = nc.Dataset (file, 'r', format='NETCDF4')

    vars = root.variables
    x = vars['x']
    y = vars['y']

    try:
        t = vars['t']
        times = t[:]
    except KeyError:
        times = [0]

    dimension_names = ['x', 'y', 'z', 't', 'dummy']

    fields = []
    for (i, time) in enumerate (times):
        field = RectilinearField (y[:], x[:], indexing='ij', units=(y.units, x.units))
        for (name, var) in vars.items ():
            if not name in dimension_names:
                field.add_field (name, var[i,:], centering='point', units=var.units)
        fields.append ((time, field))

    if vars.has_key ('t'):
        return fields
    else:
        return field


if __name__ == '__main__':
    import doctest
    doctest.testmod (optionflags=(doctest.NORMALIZE_WHITESPACE or doctest.REPORT_ONLY_FIRST_FAILURE))

