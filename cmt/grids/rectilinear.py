#! /bin/env python

"""
--------
Examples
--------
Create a grid of length 2 in the x direction, and 3 in the y direction.

    >>> g = Rectilinear ([1., 2., 4., 8.], [1., 2., 3.])
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

    >>> g = Rectilinear ([1., 2., 4., 8.], [1., 2., 3.], indexing='ij')
    >>> print g.get_x ()
    [ 1. 2. 3. 1. 2. 3. 1. 2. 3. 1. 2. 3.]
    >>> print g.get_y ()
    [ 1. 1. 1. 2. 2. 2. 4. 4. 4. 8. 8. 8.]
    >>> print g.get_shape ()
    [4 3]

    >>> print g.get_offset () # doctest: +NORMALIZE_WHITESPACE
    [ 4 8 12 16 20 24]
    >>> print g.get_connectivity () # doctest: +NORMALIZE_WHITESPACE
    [ 0 1 4 3 1 2 5 4 3 4 7 6 4 5 8 7 6 7 10 9 7 8 11 10]

Rectilinear grid of points
--------------------------

Create a grid of length 2 in the i direction, and 3 in the j direction.

    >>> g = RectilinearPoints ([1., 2., 4., 8.], [1., 2., 3.], indexing='ij', set_connectivity=True)
    >>> print g.get_x ()
    [ 1. 2. 3. 1. 2. 3. 1. 2. 3. 1. 2. 3.]
    >>> print g.get_y ()
    [ 1. 1. 1. 2. 2. 2. 4. 4. 4. 8. 8. 8.]
    >>> print g.get_shape ()
    [4 3]
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
"""

import numpy as np
from meshgrid import meshgrid
from structured import Structured, StructuredPoints

class RectilinearPoints (StructuredPoints):
    #def __init__ (self, x, y, indexing='xy', set_connectivity=False):
    def __init__ (self, x, y, **kwds):
        kwds.setdefault ('set_connectivity', False)
        kwds.setdefault ('indexing', 'xy')

        XI = np.meshgrid (x, y)
        shape = XI[0].shape
        if kwds['indexing'] == 'ij':
            shape = shape[::-1]
            self._x_coordinates = np.array (y)
            self._y_coordinates = np.array (x)
        else:
            self._x_coordinates = np.array (x)
            self._y_coordinates = np.array (y)

        #super (RectilinearPoints, self).__init__ (XI[0], XI[1], shape, indexing=indexing, set_connectivity=set_connectivity)
        super (RectilinearPoints, self).__init__ (XI[0], XI[1], shape,
                                                  **kwds)
    def get_x_coordinates (self):
        return self._x_coordinates
    def get_y_coordinates (self):
        return self._y_coordinates

class Rectilinear (RectilinearPoints, Structured):
    """
Create a rectilinear grid.

:param x: 1-D array of x-coordinates of nodes.
:type x: array_like
:param y: 1-D array of y-coordinates of nodes.
:type y: array_like
:param shape: Grid shape measured in number of nodes
:type shape: iterable

:keyword indexing: Cartesian ('xy', default) or matrix ('ij') indexing of output.
:type indexing:  string [xy|ij]

:returns: An instance of a Rectilinear grid.
:rtype: Rectilinear
    """
    #def __init__ (self, x, y, indexing='xy', set_connectivity=True):
    def __init__ (self, x, y, **kwds):
        kwds['set_connectivity'] = True 
        super (Rectilinear, self).__init__ (x, y, **kwds)
        #super (Rectilinear, self).__init__ (x, y, indexing=indexing, set_connectivity=True)

if __name__ == '__main__':
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)


