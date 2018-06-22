#! /bin/env python
"""
========
Examples
========

Create a grid that consists of 2x3 nodes using 'xy' and 'ij' indexing.

-----------
ij-indexing
-----------
Create a grid of length 2 in the i direction, and 3 in the j direction.

    >>> g = UniformRectilinear ((2,3), (1,2), (.5, 0), indexing='ij', units=('m', 'km'))
    >>> g.get_x()
    array([ 0.,  2.,  4.,  0.,  2.,  4.])
    >>> g.get_y()
    array([ 0.5,  0.5,  0.5,  1.5,  1.5,  1.5])
    >>> [g.get_x_units(), g.get_y_units()]
    ['km', 'm']
    >>> g.get_z_units()
    Traceback (most recent call last):
            ...
    IndexError: Dimension out of bounds
    >>> [g.get_coordinate_units(i) for i in [0, 1]]
    ['m', 'km']
    >>> g.get_coordinate_units(2)
    Traceback (most recent call last):
            ...
    IndexError: Dimension out of bounds
    >>> g.get_shape()
    array([2, 3])
    >>> g.get_spacing()
    array([ 1.,  2.])
    >>> g.get_origin()
    array([ 0.5,  0. ])
    >>> g.get_offset()
    array([4, 8], dtype=int32)
    >>> g.get_connectivity()
    array([0, 1, 4, 3, 1, 2, 5, 4], dtype=int32)

Uniform rectilinear grid of points
----------------------------------

Create a grid of length 2 in the i direction, and 3 in the j direction.

    >>> g = UniformRectilinearPoints ((2,3), (1,2), (.5, 0), indexing='ij', set_connectivity=True)
    >>> g.get_x()
    array([ 0.,  2.,  4.,  0.,  2.,  4.])
    >>> g.get_y()
    array([ 0.5,  0.5,  0.5,  1.5,  1.5,  1.5])
    >>> g.get_shape()
    array([2, 3])
    >>> g.get_spacing()
    array([ 1.,  2.])
    >>> g.get_origin()
    array([ 0.5,  0. ])

    >>> g.get_point_count()
    6
    >>> g.get_cell_count()
    0

The offset runs from 1 up to (and including) the number of points.

    >>> all (g.get_offset ()==np.arange (1, g.get_point_count ()+1))
    True

The connectivity runs from 0 to one less than the number of points.

    >>> all (g.get_connectivity ()==np.arange (g.get_point_count ()))
    True


1D-grid of points
-----------------
    >>> g = UniformRectilinearPoints ((5, ), (1., ), (.5,), indexing='ij', set_connectivity=True)
    >>> g.get_x()
    array([ 0.5,  1.5,  2.5,  3.5,  4.5])

3D-grid of cells
----------------

    >>> g = UniformRectilinear ((4, 3, 2), (1, 2, 3), (-1, 0, 1), indexing='ij')
    >>> g.get_x()
    array([ 1.,  4.,  1.,  4.,  1.,  4.,  1.,  4.,  1.,  4.,  1.,  4.,  1.,
            4.,  1.,  4.,  1.,  4.,  1.,  4.,  1.,  4.,  1.,  4.])
    >>> g.get_y()
    array([ 0.,  0.,  2.,  2.,  4.,  4.,  0.,  0.,  2.,  2.,  4.,  4.,  0.,
            0.,  2.,  2.,  4.,  4.,  0.,  0.,  2.,  2.,  4.,  4.])
    >>> g.get_z()
    array([-1., -1., -1., -1., -1., -1.,  0.,  0.,  0.,  0.,  0.,  0.,  1.,
            1.,  1.,  1.,  1.,  1.,  2.,  2.,  2.,  2.,  2.,  2.])

"""

import numpy as np
from .rectilinear import Rectilinear, RectilinearPoints


class UniformRectilinearPoints(RectilinearPoints):
    def __init__(self, shape, spacing, origin, **kwds):
        kwds.setdefault('indexing', 'xy')
        kwds.setdefault('set_connectivity', False)
        assert(len(shape) == len(spacing) == len(origin))

        xi = []
        for (nx, dx, x0) in zip(shape, spacing, origin):
            xi.append(np.arange(nx, dtype=np.float64) * dx + x0)

        self._spacing = np.array(spacing, dtype=np.float64)
        self._origin = np.array(origin, dtype=np.float64)

        super(UniformRectilinearPoints, self).__init__(*xi, **kwds)

    def get_spacing(self):
        """Spacing between nodes in each direction"""
        return self._spacing

    def get_origin(self):
        """Coordinates of the grid's lower-left corner"""
        return self._origin


class UniformRectilinear(UniformRectilinearPoints, Rectilinear):
    """
Create a rectilinear grid with uniform spacing in the x and y directions.

:param shape: Grid shape measured in number of nodes
:type shape: iterable
:param spacing: Spacing between nodes in each direction of a rectilinear grid.
:type spacing: iterable
:param origin: Coordinates of the lower-left corner of the grid
:type origin: iterable
:keyword indexing: Cartesian ('xy', default) or matrix ('ij') indexing of output.  See Notes for more details.
:type indexing: string ['xy'|'ij']

:returns: An instance of a UniformRectilinear grid.
:rtype: UniformRectilinear
    """
    def __init__(self, shape, spacing, origin, **kwds):
        kwds['set_connectivity'] = False
        super(UniformRectilinear, self).__init__(shape, spacing, origin,
                                                 **kwds)

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
