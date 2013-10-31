#! /bin/env python

import numpy as np

from cmt.grids.meshgrid import meshgrid
from cmt.grids.igrid import IGrid
from cmt.grids.utils import (get_default_coordinate_units,
                             get_default_coordinate_names,
                             assert_arrays_are_equal_size,
                             coordinates_to_numpy_matrix,
                             args_as_numpy_arrays)


class Error(Exception):
    pass


class DimensionError(Error):
    def __init__(self, dim0, dim1):
        try:
            self.src_dim = tuple(dim0)
        except TypeError:
            self.src_dim = (dim0)
        try:
            self.dst_dim = tuple(dim1)
        except TypeError:
            self.dst_dim = (dim1)

    def __str__(self):
        return '%s != %s' % (self.src_dim, self.dst_dim)


class AttributeError(Error):
    def __init__(self, msg):
        self.msg = msg
        self.attr = attr

    def __str__(self):
        return '%s: %s' % (self.attr, self.msg)


class UnstructuredPoints(IGrid):
    def __init__(self, *args, **kwds):
        """
        UnstructuredPoints(x0 [, x1 [, x2]])
        """
        set_connectivity = kwds.pop('set_connectivity', False)
        units = kwds.pop('units', get_default_coordinate_units(len(args)))
        coordinate_names = kwds.pop('coordinate_names',
                                    get_default_coordinate_names(len(args)))
        self._attrs = kwds.pop('attrs', {})

        assert(len(args) <= 3)
        assert(len(args) >= 1)

        args = args_as_numpy_arrays(*args)

        self._n_dims = len(args)
        self._point_count = args[0].size

        self._coords = coordinates_to_numpy_matrix(*args)
        self._units = list(units)
        self._coordinate_name = list(coordinate_names)

        if set_connectivity:
            self._connectivity = np.arange(self._point_count, dtype=np.int32)
            self._offset = self._connectivity + 1
            self._cell_count = 0

        super(UnstructuredPoints, self).__init__()

    def get_attrs(self):
        return self._attrs

    def get_dim_count(self):
        return self._n_dims

    def get_x(self):
        try:
            return self._coords[-1]
        except IndexError:
            raise IndexError('Dimension out of bounds')

    def get_y(self):
        try:
            return self._coords[-2]
        except IndexError:
            raise IndexError('Dimension out of bounds')

    def get_z(self):
        try:
            return self._coords[-3]
        except IndexError:
            raise IndexError('Dimension out of bounds')

    def get_xyz(self):
        return self._coords

    def get_point_coordinates(self, *args, **kwds):
        axis = kwds.pop('axis', None)

        assert(len(args) < 2)

        if len(args) == 0:
            inds = np.arange(self.get_point_count())
        else:
            inds = args

        if axis is None:
            axis = np.arange(self.get_dim_count())
            axis.shape = (self.get_dim_count(), 1)

        return tuple(self._coords[axis, inds])


    def get_x_units(self):
        return self.get_coordinate_units(-1)

    def get_y_units(self):
        return self.get_coordinate_units(-2)

    def get_z_units(self):
        return self.get_coordinate_units(-3)

    def set_x_units(self, units):
        try:
            self._units[-1] = units
        except IndexError:
            raise IndexError('Dimension out of bounds')

    def set_y_units(self, units):
        try:
            self._units[-2] = units
        except IndexError:
            raise IndexError('Dimension out of bounds')

    def set_z_units(self, units):
        try:
            self._units[-3] = units
        except IndexError:
            raise IndexError('Dimension out of bounds')

    def get_coordinate_units(self, i, **kwds):
        try:
            return self._units[i]
        except IndexError:
            raise IndexError('Dimension out of bounds')

    def get_coordinate_name(self, i, **kwds):
        try:
            return self._coordinate_name[i]
        except IndexError:
            raise IndexError('Dimension out of bounds')

    def get_coordinate(self, i, **kwds):
        try:
            return self._coords[i]
        except IndexError:
            raise IndexError('Dimension out of bounds')

    def get_connectivity(self):
        return self._connectivity

    def get_offset(self):
        return self._offset

    def get_point_count(self):
        return self._point_count

    def get_cell_count(self):
        return self._cell_count

    def get_vertex_count(self):
        return len(self._connectivity)


class Unstructured(UnstructuredPoints):
    """
Define a grid that consists of two trianges that share two points.

::

       (2) - (3)
      /   \  /
    (0) - (1)

Create the grid,

    >>> g = Unstructured([0, 0, 1, 1], [0, 2, 1, 3],
    ...                  connectivity=[0, 2, 1, 2, 3, 1], offset=[3, 6])
    >>> g.get_point_count()
    4
    >>> g.get_cell_count()
    2
    >>> g.get_dim_count()
    2

    >>> x = g.get_x()
    >>> type(x)
    <type 'numpy.ndarray'>
    >>> x.dtype
    dtype('float64')
    >>> print x #doctest:+NORMALIZE_WHITESPACE
    [ 0. 2. 1. 3.]

    >>> y = g.get_y()
    >>> type(y)
    <type 'numpy.ndarray'>
    >>> y.dtype
    dtype('float64')
    >>> print y #doctest:+NORMALIZE_WHITESPACE
    [ 0. 0. 1. 1.]

    >>> c = g.get_connectivity()
    >>> type(c)
    <type 'numpy.ndarray'>
    >>> c.dtype
    dtype('int32')
    >>> print c
    [0 2 1 2 3 1]

    >>> o = g.get_offset()
    >>> type(o)
    <type 'numpy.ndarray'>
    >>> o.dtype
    dtype('int32')
    >>> print o
    [3 6]

1D Grid of points
-----------------

Define a grid that consists of points in a line.

::

    (0) ----- (1) -- (2) - (3)

Create the grid,

    >>> g = Unstructured ([0., 6., 9., 11.], connectivity=[0, 1, 2, 3], offset=[1, 2, 3, 4])
    >>> g.get_point_count ()
    4
    >>> g.get_cell_count ()
    4

3D Grid
-------

Eight point that form a unit cube.

    >>> x = [0, 1, 0, 1, 0, 1, 0, 1]
    >>> y = [0, 0, 1, 1, 0, 0, 1, 1]
    >>> z = [0, 0, 0, 0, 1, 1, 1, 1]
    >>> g = Unstructured(z, y, x, connectivity=[0, 1, 2, 3, 4, 5, 6, 7], offset=[8])
    >>> g.get_point_count()
    8
    >>> g.get_cell_count()
    1
    >>> print g.get_x() #doctest:+NORMALIZE_WHITESPACE
    [ 0. 1. 0. 1. 0. 1. 0. 1.]
    >>> print g.get_y() #doctest:+NORMALIZE_WHITESPACE
    [ 0. 0. 1. 1. 0. 0. 1. 1.]
    >>> print g.get_z() #doctest:+NORMALIZE_WHITESPACE
    [ 0. 0. 0. 0. 1. 1. 1. 1.]


    """
    def __init__(self, *args, **kwds):
        set_connectivity = kwds.pop('set_connectivity', True)
        connectivity = kwds.get('connectivity', [])
        offset = kwds.get('offset', [])

        if set_connectivity:
            try:
                o = kwds['offset']
            except KeyError:
                o = args[-1]
                args = args[:-1]
            try:
                c = kwds['connectivity']
            except KeyError:
                c = args[-1]
                args = args[:-1]
            self._set_connectivity(c, o)

        kwds['set_connectivity'] = False
        super(Unstructured, self).__init__(*args, **kwds)

    def _set_connectivity(self, connectivity, offset):
        self._connectivity  = np.array(connectivity, dtype=np.int32)
        self._offset  = np.array(offset, dtype=np.int32)
        self._connectivity.shape = self._connectivity.size
        self._offset.shape = self._offset.size
        self._cell_count = self._offset.size

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)


