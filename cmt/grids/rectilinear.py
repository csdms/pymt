#! /bin/env python

"""
--------
Examples
--------
Create a grid of length 2 in the x direction, and 3 in the y direction.

    >>> g = Rectilinear([1., 2., 3.], [1., 2., 4., 8.])
    >>> assert (g.get_point_count() == 12)
    >>> assert (g.get_cell_count() == 6)
    >>> print g.get_x() #doctest:+NORMALIZE_WHITESPACE
    [ 1. 2. 4. 8. 1. 2. 4. 8. 1. 2. 4. 8.]
    >>> print g.get_y() #doctest:+NORMALIZE_WHITESPACE
    [ 1. 1. 1. 1. 2. 2. 2. 2. 3. 3. 3. 3.]
    >>> print g.get_shape()
    [3 4]

Create a grid of length 2 in the i direction, and 3 in the j direction.

    >>> g = Rectilinear([1., 2., 4., 8.], [1., 2., 3.], indexing='ij')
    >>> print g.get_x() #doctest:+NORMALIZE_WHITESPACE
    [ 1. 2. 3. 1. 2. 3. 1. 2. 3. 1. 2. 3.]
    >>> print g.get_y() #doctest:+NORMALIZE_WHITESPACE
    [ 1. 1. 1. 2. 2. 2. 4. 4. 4. 8. 8. 8.]
    >>> print g.get_shape()
    [4 3]

    >>> print g.get_offset() # doctest: +NORMALIZE_WHITESPACE
    [ 4 8 12 16 20 24]
    >>> print g.get_connectivity() # doctest: +NORMALIZE_WHITESPACE
    [ 0 1 4 3 1 2 5 4 3 4 7 6 4 5 8 7 6 7 10 9 7 8 11 10]

Rectilinear grid of points
--------------------------

Create a grid of length 2 in the i direction, and 3 in the j direction.

    >>> g = RectilinearPoints ([1., 2., 4., 8.], [1., 2., 3.], indexing='ij', set_connectivity=True)
    >>> print g.get_x() #doctest:+NORMALIZE_WHITESPACE
    [ 1. 2. 3. 1. 2. 3. 1. 2. 3. 1. 2. 3.]
    >>> print g.get_y() #doctest:+NORMALIZE_WHITESPACE
    [ 1. 1. 1. 2. 2. 2. 4. 4. 4. 8. 8. 8.]
    >>> print g.get_shape ()
    [4 3]
    >>> assert(g.get_point_count() == 12)
    >>> assert(g.get_cell_count() == 0)

The offset runs from 1 up to (and including) the number of points.

    >>> all (g.get_offset ()==np.arange (1, g.get_point_count ()+1))
    True

The connectivity runs from 0 to one less than the number of points.

    >>> all (g.get_connectivity ()==np.arange (g.get_point_count ()))
    True


1D Rectilinear grid
-------------------

    >>> g = Rectilinear([1,3,4,5,6], set_connectivity=True)
    >>> print g.get_x() #doctest:+NORMALIZE_WHITESPACE
    [ 1. 3. 4. 5. 6.]
    >>> assert(g.get_point_count () == 5)
    >>> assert(g.get_cell_count () == 4)
    >>> print g.get_connectivity()
    [0 1 1 2 2 3 3 4]
    >>> print g.get_offset()
    [2 4 6 8]


3D Rectilinear grid
-------------------
    >>> g = Rectilinear ([0, 1], [2, 3], set_connectivity=True, indexing='ij')
    >>> print g.get_x() #doctest:+NORMALIZE_WHITESPACE
    [ 2. 3. 2. 3.]
    >>> print g.get_y() #doctest:+NORMALIZE_WHITESPACE
    [ 0. 0. 1. 1.]

    >>> g = Rectilinear ([0, 1], [2, 3], [4, 5], set_connectivity=True, indexing='ij')
    >>> print g.get_x() #doctest:+NORMALIZE_WHITESPACE
    [ 4. 5. 4. 5. 4. 5. 4. 5.]
    >>> print g.get_y() #doctest:+NORMALIZE_WHITESPACE
    [ 2. 2. 3. 3. 2. 2. 3. 3.]
    >>> print g.get_z() #doctest:+NORMALIZE_WHITESPACE
    [ 0. 0. 0. 0. 1. 1. 1. 1.]
    >>> print g.get_point_count()
    8
    >>> print g.get_cell_count()
    1

    >>> g = Rectilinear([0, 1, 2, 3], [4, 5, 6], [7, 8], set_connectivity=True, indexing='ij')
    >>> print g.get_x() #doctest:+NORMALIZE_WHITESPACE
    [ 7. 8. 7. 8. 7. 8. 7. 8. 7. 8. 7. 8. 7. 8. 7. 8. 7. 8. 7. 8. 7. 8. 7. 8.]
    >>> print g.get_shape()
    [4 3 2]
    >>> x = g.get_x()
    >>> x.shape = g.get_shape()

"""

import numpy as np
from cmt.grids.meshgrid import meshgrid
from structured import Structured, StructuredPoints

class RectilinearPoints (StructuredPoints):
    def __init__ (self, *args, **kwds):
        kwds.setdefault('set_connectivity', False)
        kwds.setdefault('indexing', 'xy')

        n_dim = len(args)
        assert(n_dim >= 1)
        assert(n_dim <= 3)

        coords = []
        for arg in args:
            coords.append(np.array(arg, dtype=np.float64))

        if n_dim > 1:
            #if kwds['indexing'] == 'xy':
            #    XI = meshgrid (*coords[::-1], indexing='ij')[::-1]
            #else:
            XI = meshgrid(*coords, indexing='ij')
        else:
            XI = [np.array (args[0], dtype=np.float64)]

        shape = XI[0].shape

        #if kwds['indexing'] == 'xy':
        #    coords = coords[::-1]

        self._x_coordinates = np.array(coords[-1], dtype=np.float64)
        try:
            self._y_coordinates = np.array(coords[-2], dtype=np.float64)
        except IndexError:
            pass
            #self._y_coordinates = np.zeros (1, dtype=np.float64)
        try:
            self._z_coordinates = np.array(coords[-3], dtype=np.float64)
        except IndexError:
            pass
            #self._z_coordinates = np.zeros (1, dtype=np.float64)

        args = XI + [shape]
        super(RectilinearPoints, self).__init__ (*args, **kwds)


    def get_x_coordinates (self):
        """
        >>> g = Rectilinear ([0, 1], [2, 3], [4, 5], set_connectivity=True, indexing='ij')
        >>> print g.get_x_coordinates ()
        [ 4.  5.]
        """
        return self._x_coordinates
    def get_y_coordinates (self):
        """
        >>> g = Rectilinear ([0, 1], [2, 3], [4, 5], set_connectivity=True, indexing='ij')
        >>> print g.get_y_coordinates ()
        [ 2.  3.]
        """
        return self._y_coordinates
    def get_z_coordinates(self):
        """
        >>> g = Rectilinear ([0, 1], [2, 3], [4, 5], set_connectivity=True, indexing='ij')
        >>> print g.get_z_coordinates ()
        [ 0.  1.]
        """
        return self._z_coordinates
    def get_xyz_coordinates(self):
        return (self.get_x_coordinates (), self.get_y_coordinates (),
                self.get_z_coordinates ())

    def get_axis_coordinates(self, axis=None, indexing='ij'):
        #assert (indexing in ['xy', 'ij'])
        assert(indexing == 'ij')

        if axis is None:
            coords = [self.get_x_coordinates (),
                      self.get_y_coordinates (),
                      self.get_z_coordinates ()]
            if indexing == 'ij':
                return coords[::-1]
            else:
                return coords
        else:
            n_dims = self.get_dim_count ()
            assert (axis < n_dims)

            if indexing == 'ij':
                axis = n_dims - axis - 1

            if axis == 0:
                return self.get_x_coordinates ()
            elif axis == 1:
                return self.get_y_coordinates ()
            elif axis == 2:
                return self.get_z_coordinates ()

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
    def __init__ (self, *args, **kwds):
        kwds['set_connectivity'] = True 
        super (Rectilinear, self).__init__ (*args, **kwds)

if __name__ == '__main__':
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)


