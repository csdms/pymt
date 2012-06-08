#! /bin/env python

import numpy as np
from meshgrid import meshgrid
from igrid import IGrid, IField

class Error (Exception):
    pass
class DimensionError (Error):
    def __init__ (self, dim0, dim1):
        try:
            self.src_dim = tuple (dim0)
        except TypeError:
            self.src_dim = (dim0)
        try:
            self.dst_dim = tuple (dim1)
        except TypeError:
            self.dst_dim = (dim1)
    def __str__ (self):
        return '%s != %s' % (self.src_dim, self.dst_dim)
class AttributeError (Error):
    def __init__ (self, msg):
        self.msg = msg
        self.attr = attr
    def __str__ (self):
        return '%s: %s' % (self.attr, self.msg)

class UnstructuredPoints (IGrid):
    def __init__ (self, x, y, set_connectivity=False,
                  units=['-', '-', '-']):
        #super (UnstructuredPoints, self).__init__ (x, y, [], [])

        assert (len (x) == len (y))

        x = np.array (x, dtype=np.float64)
        y = np.array (y, dtype=np.float64)
        x.shape = x.size
        y.shape = y.size

        self._point_count = x.size

        self._coords = (np.zeros (x.shape, dtype=np.float64), y, x)

        for coord in self._coords:
            coord.shape = coord.size

        if set_connectivity:
            self._connectivity = np.arange (self._point_count, dtype=np.int32)
            self._offset = self._connectivity + 1
            self._cell_count = 0

        #self._units = ['-']*(3-len (units)) + list (units)
        self._units = list (units)
        #self._units = units[::-1]

        super (UnstructuredPoints, self).__init__ ()

    def get_x (self):
        return self._coords[-1]
    def get_y (self):
        return self._coords[-2]
    def get_z (self):
        return self._coords[0]
    def get_x_units (self):
        try:
            return self._units[-1]
        except IndexError:
            return '-'
    def get_y_units (self):
        try:
            return self._units[-2]
        except IndexError:
            return '-'
    def get_z_units (self):
        try:
            return self._units[-3]
        except IndexError:
            return '-'
    def set_x_units (self, units):
        try:
            self._units[-1] = units
        except IndexError:
            pass
    def set_y_units (self, units):
        try:
            self._units[-2] = units
        except IndexError:
            pass
    def set_z_units (self, units):
        try:
            self._units[-3] = units
        except IndexError:
            pass
    def get_coordinate_units (self, i):
        try:
            return self._units[i]
        except IndexError:
            return '-'
    def get_connectivity (self):
        return self._connectivity
    def get_offset (self):
        return self._offset

    def get_point_count (self):
        return self._point_count
    def get_cell_count (self):
        return self._cell_count
    def get_vertex_count (self):
        return len (self._connectivity)

class Unstructured (UnstructuredPoints):
    """
Define a grid that consists of two trianges that share two points.

::

       (2) - (3)
      /   \  /
    (0) - (1)

Create the grid,

    >>> g = Unstructured ([0, 2, 1, 3], [0, 0, 1, 1], [0, 2, 1, 2, 3, 1], [3, 6])
    >>> g.get_point_count ()
    4
    >>> g.get_cell_count ()
    2

    >>> x = g.get_x ()
    >>> type (x)
    <type 'numpy.ndarray'>
    >>> x.dtype
    dtype('float64')
    >>> print x
    [ 0. 2. 1. 3.]

    >>> y = g.get_y ()
    >>> type (y)
    <type 'numpy.ndarray'>
    >>> y.dtype
    dtype('float64')
    >>> print y
    [ 0. 0. 1. 1.]

    >>> c = g.get_connectivity ()
    >>> type (c)
    <type 'numpy.ndarray'>
    >>> c.dtype
    dtype('int32')
    >>> print c
    [0 2 1 2 3 1]

    >>> o = g.get_offset ()
    >>> type (o)
    <type 'numpy.ndarray'>
    >>> o.dtype
    dtype('int32')
    >>> print o
    [3 6]
    """
    def __init__ (self, x, y, connectivity=[], offset=[], **kwds):
        set_connectivity = kwds.pop ('set_connectivity', True)
        #connectivity = kwds.pop ('connectivity', [])
        #offset = kwds.pop ('offset', [])

        if len (connectivity)>0 and set_connectivity:
            self._set_connectivity (connectivity, offset)

        kwds['set_connectivity'] = False
        super (Unstructured, self).__init__ (x, y, **kwds)

        #self._cell_count = self._offset.size

    def _set_connectivity (self, connectivity, offset):
        self._connectivity  = np.array (connectivity, dtype=np.int32)
        self._offset  = np.array (offset, dtype=np.int32)
        self._connectivity.shape = self._connectivity.size
        self._offset.shape = self._offset.size
        self._cell_count = self._offset.size

if __name__ == '__main__':
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)


