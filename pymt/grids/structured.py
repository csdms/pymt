"""
Examples
--------

Create a grid of length 2 in the x direction, and 3 in the y direction.

>>> (x, y) = np.meshgrid ([1., 2., 4., 8.], [1., 2., 3.])
>>> g = Structured(y.flatten(), x.flatten(), [3, 4])
>>> g.get_point_count()
12
>>> g.get_cell_count()
6
>>> g.get_x()
array([1., 2., 4., 8., 1., 2., 4., 8., 1., 2., 4., 8.])
>>> g.get_y()
array([1., 1., 1., 1., 2., 2., 2., 2., 3., 3., 3., 3.])
>>> g.get_shape()
array([3, 4])

Create a grid of length 2 in the i direction, and 3 in the j direction.

>>> (x, y) = np.meshgrid ([1., 2., 4., 8.], [1., 2., 3.])
>>> g = Structured (y.flatten (), x.flatten (), (3, 4), indexing='ij')
>>> g.get_x()
array([1., 2., 4., 8., 1., 2., 4., 8., 1., 2., 4., 8.])
>>> g.get_y()
array([1., 1., 1., 1., 2., 2., 2., 2., 3., 3., 3., 3.])
>>> g.get_shape()
array([3, 4])

>>> g.get_offset()
array([ 4,  8, 12, 16, 20, 24])
>>> g.get_connectivity()
array([ 0,  1,  5,  4,  1,  2,  6,  5,  2,  3,  7,  6,  4,  5,  9,  8,  5,
        6, 10,  9,  6,  7, 11, 10])

**Structured grid of points**

The same grid as the previous example but without any cells - just points.

>>> (x, y) = np.meshgrid ([1., 2., 4., 8.], [1., 2., 3.])
>>> g = StructuredPoints (y.flatten (), x.flatten (), (3, 4), indexing='ij', set_connectivity=True)
>>> g.get_x()
array([1., 2., 4., 8., 1., 2., 4., 8., 1., 2., 4., 8.])
>>> g.get_y()
array([1., 1., 1., 1., 2., 2., 2., 2., 3., 3., 3., 3.])
>>> g.get_shape()
array([3, 4])

The number of points are the same, but the number of cells is now 0.

>>> g.get_point_count()
12
>>> g.get_cell_count()
0

The offset runs from 1 up to (and including) the number of points.

>>> all (g.get_offset ()==np.arange (1, g.get_point_count ()+1))
True

The connectivity runs from 0 to one less than the number of points.

>>> all (g.get_connectivity ()==np.arange (g.get_point_count ()))
True

**1D Grid of line segments**

>>> g = Structured([-1, 2, 3, 6], (4, ))
>>> g.get_x()
array([-1.,  2.,  3.,  6.])
>>> g.get_y()
Traceback (most recent call last):
        ...
IndexError: Dimension out of bounds
>>> g.get_shape()
array([4])

>>> g.get_offset()
array([2, 4, 6])
>>> g.get_connectivity()
array([0, 1, 1, 2, 2, 3])


**3D Grid of cubes**

>>> x = [0, 1, 0, 1, 0, 1, 0, 1]
>>> y = [0, 0, 1, 1, 0, 0, 1, 1]
>>> z = [0, 0, 0, 0, 1, 1, 1, 1]

>>> g = Structured(z, y, x, (2, 2, 2))

>>> g.get_x()
array([0., 1., 0., 1., 0., 1., 0., 1.])
>>> g.get_y()
array([0., 0., 1., 1., 0., 0., 1., 1.])
>>> g.get_z()
array([0., 0., 0., 0., 1., 1., 1., 1.])

>>> g.get_connectivity()
array([0, 1, 3, 2, 4, 5, 7, 6])
>>> g.get_offset()
array([8])

>>> g = Structured(x, y, z, (2, 2, 2), ordering='ccw')
>>> g.get_connectivity()
array([1, 0, 2, 3, 5, 4, 6, 7])
"""
import warnings

import numpy as np

from pymt.grids.connectivity import get_connectivity
from pymt.grids.utils import get_default_coordinate_names, get_default_coordinate_units

from .unstructured import Unstructured, UnstructuredPoints


class StructuredPoints(UnstructuredPoints):
    def __init__(self, *args, **kwds):
        """StructuredPoints(x0 [, x1 [, x2]], shape)"""
        (coordinates, shape) = (args[:-1], args[-1])

        if len(coordinates) < 1 or len(coordinates) > 3:
            raise ValueError("number of dimensions must be between 1 and 3")

        kwds.setdefault("set_connectivity", True)
        indexing = kwds.pop("indexing", "xy")

        if indexing != "ij":
            warnings.warn("only ij indexing is supported", RuntimeWarning)
            indexing = "ij"

        coordinate_names = kwds.pop(
            "coordinate_names", get_default_coordinate_names(len(coordinates))
        )
        coordinate_units = kwds.pop(
            "units", get_default_coordinate_units(len(coordinates))
        )

        self._shape = np.array(shape, dtype=int)

        kwds["units"] = coordinate_units
        kwds["coordinate_names"] = coordinate_names

        super().__init__(*coordinates, **kwds)

    def get_shape(self, remove_singleton=False):
        """The shape of the structured grid with the given indexing.

        Use remove_singleton=False to include singleton dimensions.
        """
        shape = self._shape.copy()
        if remove_singleton:
            shape = shape[shape > 1]

        return shape

    def get_coordinate_units(self, i):
        return super().get_coordinate_units(i)

    def get_coordinate_name(self, i):
        return super().get_coordinate_name(i)

    def get_coordinate(self, i):
        return super().get_coordinate(i)

    def get_point_coordinates(self, *args, **kwds):
        return super().get_point_coordinates(*args, **kwds)


class Structured(StructuredPoints, Unstructured):
    """Create a structured rectilinear grid.

    Parameters
    ----------
    x: ndarray
        1-D array of x-coordinates of nodes.
    y: ndarray
        1-D array of y-coordinates of nodes.
    shape: tuple of int
        Shape of the grid.
    indexing: {'xy', 'ij'}, optional
        Cartesian('xy', default) or matrix('ij') indexing of output.

    Returns
    -------
    Structured
        An instance of a Structured grid.
    """

    def __init__(self, *args, **kwds):
        kwds.setdefault("indexing", "xy")
        kwds.setdefault("set_connectivity", True)
        ordering = kwds.pop("ordering", "cw")
        if ordering not in ["cw", "ccw"]:
            raise TypeError("ordering not understood (valid choices are 'cw' or 'ccw')")

        shape = args[-1]

        if kwds["set_connectivity"]:
            (c, o) = get_connectivity(shape, ordering=ordering, with_offsets=True)
            self._set_connectivity(c, o)
            kwds["set_connectivity"] = False

        super().__init__(*args, **kwds)


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
