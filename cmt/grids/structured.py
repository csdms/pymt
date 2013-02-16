#! /bin/env python

"""
Examples
========

Create a grid of length 2 in the x direction, and 3 in the y direction.

    >>> (x, y) = np.meshgrid ([1., 2., 4., 8.], [1., 2., 3.])
    >>> g = Structured (x.flatten (), y.flatten (), [3, 4])
    >>> g.get_point_count ()
    12
    >>> g.get_cell_count ()
    6
    >>> print g.get_x ()
    [ 1. 2. 4. 8. 1. 2. 4. 8. 1. 2. 4. 8.]
    >>> print g.get_y ()
    [ 1. 1. 1. 1. 2. 2. 2. 2. 3. 3. 3. 3.]
    >>> print g.get_shape ()
    [3 4]

Create a grid of length 2 in the i direction, and 3 in the j direction.

    >>> (x, y) = np.meshgrid ([1., 2., 4., 8.], [1., 2., 3.])
    >>> g = Structured (y.flatten (), x.flatten (), (3, 4), indexing='ij')
    >>> print g.get_x ()
    [ 1. 2. 4. 8. 1. 2. 4. 8. 1. 2. 4. 8.]
    >>> print g.get_y ()
    [ 1. 1. 1. 1. 2. 2. 2. 2. 3. 3. 3. 3.]
    >>> print g.get_shape ()
    [3 4]

    >>> print g.get_offset () # doctest: +NORMALIZE_WHITESPACE
    [ 4 8 12 16 20 24]
    >>> print g.get_connectivity () # doctest: +NORMALIZE_WHITESPACE
    [ 0 1 5 4 1 2 6 5 2 3 7 6 4 5 9 8 5 6 10 9 6 7 11 10]

Structured grid of points
-------------------------

The same grid as the previous example but without any cells - just points.

    >>> (x, y) = np.meshgrid ([1., 2., 4., 8.], [1., 2., 3.])
    >>> g = StructuredPoints (y.flatten (), x.flatten (), (3, 4), indexing='ij', set_connectivity=True)
    >>> print g.get_x ()
    [ 1. 2. 4. 8. 1. 2. 4. 8. 1. 2. 4. 8.]
    >>> print g.get_y ()
    [ 1. 1. 1. 1. 2. 2. 2. 2. 3. 3. 3. 3.]
    >>> print g.get_shape ()
    [3 4]

The number of points are the same, but the number of cells is now 0.

    >>> g.get_point_count ()
    12
    >>> g.get_cell_count ()
    0

The offset runs from 1 up to (and including) the number of points.

    >>> all (g.get_offset ()==np.arange (1, g.get_point_count ()+1))
    True

The connectivity runs from 0 to one less than the number of points.

    >>> all (g.get_connectivity ()==np.arange (g.get_point_count ()))
    True

1D Grid of line segments
------------------------

    >>> g = Structured ([-1, 2, 3, 6], (4, ))
    >>> print g.get_x ()
    [-1. 2. 3. 6.]
    >>> print g.get_y ()
    [ 0. 0. 0. 0.]
    >>> print g.get_shape ()
    [4]

    >>> print g.get_offset () # doctest: +NORMALIZE_WHITESPACE
    [2 4 6]
    >>> print g.get_connectivity () # doctest: +NORMALIZE_WHITESPACE
    [0 1 1 2 2 3]


3D Grid of cubes
----------------

    >>> x = [0, 1, 0, 1, 0, 1, 0, 1]
    >>> y = [0, 0, 1, 1, 0, 0, 1, 1]
    >>> z = [0, 0, 0, 0, 1, 1, 1, 1]

    >>> g = Structured (x, y, z, (2, 2, 2))

    >>> print g.get_x ()
    [ 0. 1. 0. 1. 0. 1. 0. 1.]
    >>> print g.get_y ()
    [ 0. 0. 1. 1. 0. 0. 1. 1.]
    >>> print g.get_z ()
    [ 0. 0. 0. 0. 1. 1. 1. 1.]

    >>> print g.get_connectivity ()
    [0 1 3 2 4 5 7 6]
    >>> print g.get_offset ()
    [8]

    >>> g = Structured (x, y, z, (2, 2, 2), ordering='ccw')
    >>> print g.get_connectivity ()
    [1 0 2 3 5 4 6 7]

"""
import numpy as np
from meshgrid import meshgrid
from igrid import IGrid, IField
from unstructured import Unstructured, UnstructuredPoints
from connectivity import get_connectivity

def _default_coordinate_names (n_dims, indexing='xy'):
    default_names = ['x', 'y', 'z']
    names = default_names[:n_dims]
    if indexing == 'ij':
        names = names[::-1]
    return names

def _default_coordinate_units (n_dims, indexing='xy'):
    return ['-'] * n_dims

class StructuredPoints (UnstructuredPoints):
    def __init__ (self, *args, **kwds):
        kwds.setdefault ('set_connectivity', True)
        indexing = kwds.pop ('indexing', 'xy')
        coordinate_names = kwds.pop (
            'coordinate_names', _default_coordinate_names (len (args) - 1,
                                                           indexing=indexing))
        coordinate_units = kwds.pop (
            'units', _default_coordinate_units (len (args) - 1,
                                                indexing=indexing))

        self._shape = np.array (args[-1], dtype=np.int64)

        coords = [arg for arg in args[:-1]]
        if indexing == 'ij':
            coords = coords[::-1]
            coordinate_names = coordinate_names[::-1]
            coordinate_units = coordinate_units[::-1]

        assert (len (coords) >= 1)
        assert (len (coords) <= 3)

        kwds['units'] = coordinate_units
        kwds['coordinate_names'] = coordinate_names

        super (StructuredPoints, self).__init__ (*coords, **kwds)

    def get_shape (self, remove_singleton=False, indexing='ij'):
        """The shape of the structured grid with the given indexing.
        
        Use remove_singleton=False to include singleton dimensions.
        """
        shape = self._shape.copy ()
        if remove_singleton:
            shape = shape[shape>1]

        if indexing == 'xy':
            shape = shape[::-1]

        return shape

    def get_coordinate_units (self, i, indexing='xy'):
        if indexing == 'ij':
            return super (StructuredPoints, self).get_coordinate_units (
                self.get_dim_count () - (i+1))
        else:
            return super (StructuredPoints, self).get_coordinate_units (i)
    def get_coordinate_name (self, i, indexing='xy'):
        if indexing == 'ij':
            return super (StructuredPoints, self).get_coordinate_name (
                self.get_dim_count () - (i+1))
        else:
            return super (StructuredPoints, self).get_coordinate_name (i)
    def get_coordinate (self, i, indexing='xy'):
        if indexing == 'ij':
            return super (StructuredPoints, self).get_coordinate (
                self.get_dim_count () - (i+1))
        else:
            return super (StructuredPoints, self).get_coordinate (i)
    def get_point_coordinates (self, *args, **kwds):
        axes = np.array ([kwds.get ('axis', [])], dtype=np.int64)
        indexing = kwds.pop ('indexing', 'xy')

        if indexing == 'ij' and len (axes) > 0:
            kwds['axis'] = self.get_dim_count () - (axes + 1)
        return super (StructuredPoints, self).get_point_coordinates (*args, **kwds)


class Structured (StructuredPoints, Unstructured):
    """
Create a structured rectilinear grid.

:param x: 1-D array of x-coordinates of nodes.
:type x: array_like
:param y: 1-D array of y-coordinates of nodes.
:type y: array_like
:param shape: 1-D array of y-coordinates of nodes.

:keyword indexing: Cartesian ('xy', default) or matrix ('ij') indexing of output.
:type indexing:  string [xy|ij]

:returns: An instance of a Structured grid.
:rtype: Structured
    shape : array_like


    """
    def __init__ (self, *args, **kwds):
        kwds.setdefault ('indexing', 'xy')
        kwds.setdefault ('set_connectivity', True)
        ordering = kwds.pop ('ordering', 'cw')
        if not ordering in ['cw', 'ccw']:
            raise TypeError ("ordering not understood (valid choices are 'cw' or 'ccw')")

        shape = args[-1]

        if kwds['set_connectivity']:
            (c, o) = get_connectivity (shape, ordering=ordering, with_offsets=True)
            self._set_connectivity (c, o)
            kwds['set_connectivity'] = False

        super (Structured, self).__init__ (*args, **kwds)

if __name__ == '__main__':
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)


