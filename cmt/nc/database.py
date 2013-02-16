#! /usr/bin/env python

import os
import string

from cmt.nc import writer_from_shape, remove_singleton, DimensionError, field_tofile
from cmt.grids import GridTypeError
from cmt.verbose import CMTLogger

logger = CMTLogger ('NcDatabase', 20)

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
    >>> os.path.isfile ('./Elevation_time_series_0000.nc')
    True

    >>> db.close ()

    """
    def open (self, path, var_name, **kwds):
        self.close ()

        (root, ext) = os.path.splitext (path)

        self._var_name = var_name
        self._path = path
        self._template = '%s_%%04d%s' % (root, ext)

    def write (self, field, **kwds):
        kwds.setdefault ('append', True)

        #logger.debug ('Number of points is %d' % field.get_point_count ())
        #logger.debug ('Number of cells is %d' % field.get_cell_count ())
        #logger.debug ('Shape of field is %s' % field.get_shape ())

        if kwds['append']:
            try:
                if (self._point_count != field.get_point_count () or
                    self._cell_count != field.get_cell_count ()):

                    self._path = self._next_file_name ()
            except AttributeError:
                pass

            self._point_count = field.get_point_count ()
            self._cell_count = field.get_cell_count ()
        else:
            self._path = self._next_file_name ()

        field_tofile (field, self._path, **kwds)

    def close (self):
        try:
            del self._count
        except AttributeError:
            pass
        try:
            del self._point_count
            del self._cell_count
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

if __name__ == '__main__':
    import doctest
    doctest.testmod ()

