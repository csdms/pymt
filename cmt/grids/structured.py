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
    >>> g = Structured (x.flatten (), y.flatten (), (4, 3), indexing='ij')
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

Structured grid of points
-------------------------

The same grid as the previous example but without any cells - just points.

    >>> (x, y) = np.meshgrid ([1., 2., 4., 8.], [1., 2., 3.])
    >>> g = StructuredPoints (x.flatten (), y.flatten (), (4, 3), indexing='ij', set_connectivity=True)
    >>> print g.get_x ()
    [ 1. 2. 3. 1. 2. 3. 1. 2. 3. 1. 2. 3.]
    >>> print g.get_y ()
    [ 1. 1. 1. 2. 2. 2. 4. 4. 4. 8. 8. 8.]
    >>> print g.get_shape ()
    [4 3]

The number of points are the same, but the number of cells is not 0.

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
from igrid import IGrid, IField
from unstructured import Unstructured, UnstructuredPoints
from connectivity import get_connectivity

class StructuredPoints (UnstructuredPoints):
    #def __init__ (self, x, y, shape, indexing='xy', set_connectivity=True, **kwargs):
    def __init__ (self, x, y, shape, **kwds):
        kwds.setdefault ('set_connectivity', True)
        indexing = kwds.pop ('indexing', 'xy')

        x = np.array (x, dtype=np.float64)
        y = np.array (y, dtype=np.float64)

        assert (len (x) == len (y))
        assert (x.size == np.prod (shape))

        if indexing == 'xy':
            x.shape = shape
            y.shape = shape
        else:
            (y, x) = (x.reshape (shape[::-1]).T.copy (),
                      y.reshape (shape[::-1]).T.copy ())

        self._shape = np.array (x.shape, dtype=np.int64)

        super (StructuredPoints, self).__init__ (x, y, **kwds)

        #self._shape = np.array (x.shape, dtype=np.int64)

    def get_shape (self):
        """The shape of the structured grid."""
        return self._shape

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
    #def __init__ (self, x, y, shape, indexing='xy', set_connectivity=True):
    def __init__ (self, x, y, shape, **kwds):
        kwds.setdefault ('indexing', 'xy')
        kwds.setdefault ('set_connectivity', True)
        ordering = kwds.pop ('ordering', 'cw')
        if not ordering in ['cw', 'ccw']:
            raise TypeError ("ordering not understood (valid choices are 'cw' or 'ccw')")

        (c, o) = get_connectivity (shape, ordering=ordering, with_offsets=True)

        super (Structured, self).__init__ (x, y, shape, connectivity=c,
                                           offset=o, **kwds)

if __name__ == '__main__':
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)


