#! /usr/bin/env python

import os
import string

from cmt.nc import writer_from_shape, remove_singleton, DimensionError
from cmt.grids import GridTypeError

class IDatabase (object):
    def __init__ (self):
        pass
    def open (self, path, var_name):
        pass
    def write (self, field):
        pass
    def close (self):
        pass

class Database (IDatabase):
    """
    >>> from cmt.grids import RasterField
    >>> import numpy as np

Create field and add some data to it that we will write to a NetCDF file
database.

    >>> data = np.arange (6.)

    >>> field = RasterField ((3,2), (1.,1.), (0.,0.))
    >>> field.add_field ('Elevation', data, centering='point')

Create database of 'Elevation' values. Data are written to the NetCDF file
Elevation_time_series.nc.

    >>> db = Database ()
    >>> db.open ('Elevation_time_series.nc', 'Elevation')
    >>> db.write (field)
    Imported Nio version: 1.4.0
    >>> os.path.isfile ('./Elevation_time_series.nc')
    True

Append data to the NetCDF file.

    >>> data *= 2.
    >>> db.write (field)

Create a new field and write the data to the database. Since the size of the 
field has changed, the data will be written to a new file,
Elevation_time_series_0000.nc.

    >>> field = RasterField ((3,3), (1.,1.), (0.,0.))
    >>> data = np.arange (9.)
    >>> field.add_field ('Elevation', data, centering='point')

    >>> db.write (field)
    Imported Nio version: 1.4.0
    >>> os.path.isfile ('./Elevation_time_series_0000.nc')
    True

    >>> db.close ()

    """
    def open (self, path, var_name, **kwargs):
        self.close ()

        (root, ext) = os.path.splitext (path)

        self._var_name = var_name
        self._path = path
        self._template = '%s_%%04d%s' % (root, ext)

    def write (self, field):
        array = field.get_field (self._var_name)

        try:
            self._writer.write (array)
        except AttributeError:
            # There is no _writer. Create a new one based of the shape of field.
            try:
                spacing = remove_singleton (field.get_spacing (), field.get_shape ())
                shape = remove_singleton (field.get_shape (), field.get_shape ())
            except BadGridtypeError:
                print 'NetCDF only supports uniform rectilinear grids'
                raise

            writer = writer_from_shape (shape)
            try:
                self._writer = writer (shape, spacing)
            except RankError:
                print 'Unable to create writer'
                raise
            self._writer.open (self._path, self._var_name)
            self.write (field)
        except DimensionError:
            # Error is raised if the dimension has changed. If it has, write the
            # array to a new file rather than appending to the currently opened
            # file.
            self.close ()
            new_path = self._next_file_name ()
            self.open (new_path, self._var_name)

            self.write (field)

    def close (self):
        try:
            self._writer.close ()
            del self._writer
        except AttributeError:
            pass
        try:
            del self._count
        except AttributeError:
            pass

    def _next_file_name (self):
        try:
            next_file_name = self._template % self._count
        except AttributeError:
            self._count = 0
            next_file_name = self._template % self._count
        finally:
            self._count += 1

        return next_file_name

