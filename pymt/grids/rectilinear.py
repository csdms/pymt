"""
Examples
--------

Create a grid of length 2 in the x direction, and 3 in the y direction.

>>> g = Rectilinear([1., 2., 3.], [1., 2., 4., 8.])
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

>>> g = Rectilinear([1., 2., 4., 8.], [1., 2., 3.], indexing='ij')
>>> g.get_x()
array([1., 2., 3., 1., 2., 3., 1., 2., 3., 1., 2., 3.])
>>> g.get_y()
array([1., 1., 1., 2., 2., 2., 4., 4., 4., 8., 8., 8.])
>>> g.get_shape()
array([4, 3])

>>> g.get_offset()
array([ 4,  8, 12, 16, 20, 24])
>>> g.get_connectivity()
array([ 0,  1,  4,  3,  1,  2,  5,  4,  3,  4,  7,  6,  4,  5,  8,  7,  6,
        7, 10,  9,  7,  8, 11, 10])

**Rectilinear grid of points**

Create a grid of length 2 in the i direction, and 3 in the j direction.

>>> g = RectilinearPoints ([1., 2., 4., 8.], [1., 2., 3.], indexing='ij', set_connectivity=True)
>>> g.get_x()
array([1., 2., 3., 1., 2., 3., 1., 2., 3., 1., 2., 3.])
>>> g.get_y()
array([1., 1., 1., 2., 2., 2., 4., 4., 4., 8., 8., 8.])
>>> g.get_shape ()
array([4, 3])
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


**1D Rectilinear grid**

>>> g = Rectilinear([1,3,4,5,6], set_connectivity=True)
>>> g.get_x()
array([1., 3., 4., 5., 6.])
>>> g.get_point_count()
5
>>> g.get_cell_count()
4
>>> g.get_connectivity()
array([0, 1, 1, 2, 2, 3, 3, 4])
>>> g.get_offset()
array([2, 4, 6, 8])


**3D Rectilinear grid**

>>> g = Rectilinear ([0, 1], [2, 3], set_connectivity=True, indexing='ij')
>>> g.get_x()
array([2., 3., 2., 3.])
>>> g.get_y()
array([0., 0., 1., 1.])

>>> g = Rectilinear ([0, 1], [2, 3], [4, 5], set_connectivity=True, indexing='ij')
>>> g.get_x()
array([4., 5., 4., 5., 4., 5., 4., 5.])
>>> g.get_y()
array([2., 2., 3., 3., 2., 2., 3., 3.])
>>> g.get_z()
array([0., 0., 0., 0., 1., 1., 1., 1.])
>>> g.get_point_count()
8
>>> g.get_cell_count()
1

>>> g = Rectilinear([0, 1, 2, 3], [4, 5, 6], [7, 8], set_connectivity=True, indexing='ij')
>>> g.get_x()
array([7., 8., 7., 8., 7., 8., 7., 8., 7., 8., 7., 8., 7., 8., 7., 8., 7.,
       8., 7., 8., 7., 8., 7., 8.])
>>> g.get_shape()
array([4, 3, 2])
>>> x = g.get_x()
>>> x.shape = g.get_shape()
"""

import numpy as np

from pymt.grids.meshgrid import meshgrid

from .structured import Structured, StructuredPoints


class RectilinearPoints(StructuredPoints):
    def __init__(self, *args, **kwds):
        kwds.setdefault("set_connectivity", False)
        kwds.setdefault("indexing", "xy")

        n_dim = len(args)
        if n_dim < 1 or n_dim > 3:
            raise ValueError("number of dimensions must be between 1 and 3")

        coords = []
        for arg in args:
            coords.append(np.array(arg, dtype=np.float64))

        if n_dim > 1:
            XI = meshgrid(*coords, indexing="ij")
        else:
            XI = [np.array(args[0], dtype=np.float64)]

        shape = XI[0].shape

        self._x_coordinates = np.array(coords[-1], dtype=np.float64)
        try:
            self._y_coordinates = np.array(coords[-2], dtype=np.float64)
        except IndexError:
            pass

        try:
            self._z_coordinates = np.array(coords[-3], dtype=np.float64)
        except IndexError:
            pass

        args = XI + [shape]
        super().__init__(*args, **kwds)

    def get_x_coordinates(self):
        """

        Examples
        --------

        >>> g = Rectilinear([0, 1], [2, 3], [4, 5], set_connectivity=True, indexing='ij')
        >>> g.get_x_coordinates()
        array([4., 5.])
        """
        return self._x_coordinates

    def get_y_coordinates(self):
        """
        Examples
        --------

        >>> g = Rectilinear([0, 1], [2, 3], [4, 5], set_connectivity=True, indexing='ij')
        >>> g.get_y_coordinates()
        array([2., 3.])
        """
        return self._y_coordinates

    def get_z_coordinates(self):
        """
        Examples
        --------

        >>> g = Rectilinear([0, 1], [2, 3], [4, 5], set_connectivity=True, indexing='ij')
        >>> g.get_z_coordinates()
        array([0., 1.])
        """
        return self._z_coordinates

    def get_xyz_coordinates(self):
        return (
            self.get_x_coordinates(),
            self.get_y_coordinates(),
            self.get_z_coordinates(),
        )

    def get_axis_coordinates(self, axis=None, indexing="ij"):
        if indexing != "ij":
            raise ValueError("only ij indexing is supported")

        if axis is None:
            return [
                self.get_z_coordinates(),
                self.get_y_coordinates(),
                self.get_x_coordinates(),
            ]
        else:
            n_dims = self.get_dim_count()
            if axis >= n_dims:
                raise ValueError("axis is greater than number of dimensions")

            axis = n_dims - axis - 1

            if axis == 0:
                return self.get_x_coordinates()
            elif axis == 1:
                return self.get_y_coordinates()
            elif axis == 2:
                return self.get_z_coordinates()


class Rectilinear(RectilinearPoints, Structured):
    """Create a rectilinear grid.

    Parameters
    ----------
    x: ndarray
        1-D array of x-coordinates of nodes.
    y: ndarray
        1-D array of y-coordinates of nodes.
    shape: tuple of int
        Grid shape measured in number of nodes
    indexing: {'xy', 'ij'}, optional
        Cartesian ('xy', default) or matrix ('ij') indexing of output.

    Returns
    -------
    Rectilinear
        An instance of a Rectilinear grid.
    """

    def __init__(self, *args, **kwds):
        kwds["set_connectivity"] = True
        super().__init__(*args, **kwds)


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
