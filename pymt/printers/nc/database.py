#! /usr/bin/env python

import os

from .ugrid import close as ugrid_close
from .write import field_tofile


class IDatabase:
    def __init__(self):
        pass

    def open(self, path, var_name, **kwds):
        pass

    def write(self, field, **kwds):
        pass

    def close(self):
        pass


def field_changed_size(field, n_points, n_cells):
    return n_points != field.get_point_count() or n_cells != field.get_cell_count()


class Database(IDatabase):
    def open(self, path, var_name, **kwds):
        self.close()

        (root, ext) = os.path.splitext(path)

        self._var_name = var_name
        self._path = path
        self._template = "%s_%%04d%s" % (root, ext)

        self._point_count = None
        self._cell_count = None

    def write(self, field, **kwds):
        kwds.setdefault("append", True)

        if kwds["append"]:
            if self._point_count is not None and self._cell_count is not None:
                if field_changed_size(field, self._point_count, self._cell_count):
                    self._path = self._next_file_name()

            self._point_count = field.get_point_count()
            self._cell_count = field.get_cell_count()
        else:
            self._path = self._next_file_name()

        field_tofile(field, self._path, **kwds)

    def close(self):
        try:
            del self._count
        except AttributeError:
            pass
        try:
            del self._point_count
            del self._cell_count
        except AttributeError:
            pass
        try:
            ugrid_close(self._path)
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
