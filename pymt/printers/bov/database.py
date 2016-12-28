#! /bin/env python

import os

from .bov_io import tofile


class IDatabase(object):
    def __init__(self):
        pass

    def open(self, path, var_name):
        pass

    def write(self, field):
        pass

    def close(self):
        pass


class Database(IDatabase):
    """
    >>> import numpy as np
    >>> from pymt.grids import RasterField

    >>> data = np.arange (6.)

    >>> field = RasterField ((3,2), (1.,1.), (0.,0.))
    >>> field.add_field ('Elevation', data, centering='point')

    >>> db = Database ()
    >>> db.open ('Bov_database.bov', 'Elevation')

Write the field to the database. Since BOV files only store one variable,
append the variable name to the file name.

    >>> db.write (field)
    >>> os.path.isfile ('Bov_database_0000.bov')
    True

    >>> data *= 2.
    >>> db.write (field)
    >>> os.path.isfile ('Bov_database_0001.bov')
    True

    >>> data *= 2.
    >>> db.write (field)
    >>> os.path.isfile ('Bov_database_0002.bov')
    True

    >>> db.close ()
    """
    def __init__(self):
        super(Database, self).__init__()

        self._var_name = ''
        self._path = ''
        self._template = ''
        self._options = {}

    def open(self, path, var_name, **kwargs):
        self.close()

        (root, ext) = os.path.splitext(path)

        self._var_name = var_name
        self._path = path
        self._template = '%s_%%04d%s' % (root, ext)

        self._options.update(**kwargs)

    def write(self, field):
        file_name = self._next_file_name()
        tofile(file_name, field, no_clobber=False, options=self._options)

    def close(self):
        try:
            del self._count
        except AttributeError:
            pass

    def _next_file_name(self):
        try:
            next_file_name = self._template % self._count
        except AttributeError:
            self._count = 0
            next_file_name = self._template % self._count
        finally:
            self._count += 1

        return next_file_name
