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
    [ 1 0 3 4 2 1 4 5 4 3 6 7 5 4 7 8 7 6 9 10 8 7 10 11]

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
    def __init__ (self, x, y, indexing='xy', set_connectivity=False):
        XI = np.meshgrid (x, y)
        shape = XI[0].shape
        if indexing == 'ij':
            shape = shape[::-1]
        super (RectilinearPoints, self).__init__ (XI[0], XI[1], shape, indexing=indexing, set_connectivity=set_connectivity)

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
    def __init__ (self, x, y, indexing='xy', set_connectivity=True):
        super (Rectilinear, self).__init__ (x, y, indexing=indexing, set_connectivity=True)

if __name__ == '__main__':
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)


