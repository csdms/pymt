#! /bin/env python
import numpy as np

from .igrid import IGrid
from .utils import (
    args_as_numpy_arrays,
    coordinates_to_numpy_matrix,
    get_default_coordinate_names,
    get_default_coordinate_units,
)

MAXSIZE = np.iinfo(int).max


class UnstructuredPoints(IGrid):
    def __init__(self, *args, **kwds):
        """
        UnstructuredPoints(x0 [, x1 [, x2]])
        """
        set_connectivity = kwds.pop("set_connectivity", False)
        units = kwds.pop("units", get_default_coordinate_units(len(args)))
        coordinate_names = kwds.pop(
            "coordinate_names", get_default_coordinate_names(len(args))
        )
        self._attrs = kwds.pop("attrs", {})

        if len(args) < 1 or len(args) > 3:
            raise ValueError("number of arguments must be between 1 and 3")

        args = args_as_numpy_arrays(*args)

        self._n_dims = len(args)
        self._point_count = args[0].size

        self._coords = coordinates_to_numpy_matrix(*args)
        self._units = np.array(units)
        self._coordinate_name = np.array(coordinate_names)

        if set_connectivity:
            self._connectivity = np.arange(self._point_count, dtype=int)
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
            raise IndexError("Dimension out of bounds")

    def get_y(self):
        try:
            return self._coords[-2]
        except IndexError:
            raise IndexError("Dimension out of bounds")

    def get_z(self):
        try:
            return self._coords[-3]
        except IndexError:
            raise IndexError("Dimension out of bounds")

    def get_xyz(self):
        return self._coords

    def get_point_coordinates(self, *args, **kwds):
        axis = kwds.pop("axis", None)

        if len(args) == 0:
            inds = np.arange(self.get_point_count())
        elif len(args) == 1:
            inds = args
        else:
            raise ValueError("number of args must be 0 or 1")

        if axis is None:
            axis = np.arange(self.get_dim_count())
            axis.shape = (self.get_dim_count(), 1)

        return tuple(self._coords[axis, inds])

    def get_axis_coordinates(self, axis=None, indexing="ij"):
        if indexing != "ij":
            raise ValueError("only ij indexing is supported")
        if axis is not None and axis >= self.get_dim_count():
            raise ValueError("value for axis exceeds number of dimensions")

        if axis is None:
            return self._coords
        else:
            return self._coords[axis]

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
            raise IndexError("Dimension out of bounds")

    def set_y_units(self, units):
        try:
            self._units[-2] = units
        except IndexError:
            raise IndexError("Dimension out of bounds")

    def set_z_units(self, units):
        try:
            self._units[-3] = units
        except IndexError:
            raise IndexError("Dimension out of bounds")

    def get_coordinate_units(self, i):
        try:
            return self._units[i]
        except IndexError:
            raise IndexError("Dimension out of bounds")

    def get_coordinate_name(self, i):
        try:
            return self._coordinate_name[i]
        except IndexError:
            raise IndexError("Dimension out of bounds")

    def get_coordinate(self, i):
        try:
            return self._coords[i]
        except IndexError:
            raise IndexError("Dimension out of bounds")

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

    def get_max_vertices(self):
        nodes_per_cell = np.diff(self._offset)
        return max(self._offset[0], nodes_per_cell.max())

    def get_connectivity_as_matrix(self, fill_val=MAXSIZE):
        nodes_per_cell = np.diff(self._offset)

        max_vertices = max(self._offset[0], nodes_per_cell.max())
        matrix = np.empty((self._cell_count, max_vertices), dtype=int)

        offset = self._offset[0]
        matrix[0, :offset] = self._connectivity[:offset]
        matrix[0, offset:] = fill_val
        for (cell, offset) in enumerate(self._offset[:-1]):
            n_vertices = nodes_per_cell[cell]
            matrix[cell + 1, :n_vertices] = self._connectivity[
                offset : offset + n_vertices
            ]
            matrix[cell + 1, n_vertices:] = fill_val

        return (matrix, fill_val)

    def nodes_per_cell(self):
        offsets = np.empty(self.get_cell_count() + 1, dtype=int)
        (offsets[0], offsets[1:]) = (0, self._offset[:])

        return np.diff(offsets)

    def reverse_element_ordering(self):
        last_offset = 0
        for offset in self._offset:
            c = self._connectivity[last_offset:offset].copy()
            self._connectivity[last_offset:offset] = c[::-1]
            last_offset = offset


class Unstructured(UnstructuredPoints):
    r"""
    Define a grid that consists of two trianges that share two points::

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

    >>> g.get_x()
    array([ 0.,  2.,  1.,  3.])

    >>> g.get_y()
    array([ 0.,  0.,  1.,  1.])

    >>> g.get_connectivity()
    array([0, 2, 1, 2, 3, 1])

    >>> g.get_offset()
    array([3, 6])


    Define a grid that consists of points in a line::

        (0) ----- (1) -- (2) - (3)

    Create the grid,

    >>> g = Unstructured ([0., 6., 9., 11.], connectivity=[0, 1, 2, 3], offset=[1, 2, 3, 4])
    >>> g.get_point_count ()
    4
    >>> g.get_cell_count ()
    4

    Eight point that form a unit cube.

    >>> x = [0, 1, 0, 1, 0, 1, 0, 1]
    >>> y = [0, 0, 1, 1, 0, 0, 1, 1]
    >>> z = [0, 0, 0, 0, 1, 1, 1, 1]
    >>> g = Unstructured(z, y, x, connectivity=[0, 1, 2, 3, 4, 5, 6, 7], offset=[8])
    >>> g.get_point_count()
    8
    >>> g.get_cell_count()
    1
    >>> g.get_x()
    array([ 0.,  1.,  0.,  1.,  0.,  1.,  0.,  1.])
    >>> g.get_y()
    array([ 0.,  0.,  1.,  1.,  0.,  0.,  1.,  1.])
    >>> g.get_z()
    array([ 0.,  0.,  0.,  0.,  1.,  1.,  1.,  1.])
    """

    def __init__(self, *args, **kwds):
        set_connectivity = kwds.pop("set_connectivity", True)
        connectivity = kwds.pop("connectivity", None)
        offset = kwds.pop("offset", None)

        if set_connectivity:
            if offset is None:
                offset, args = args[-1], args[:-1]
            if connectivity is None:
                connectivity, args = args[-1], args[:-1]
            self._set_connectivity(connectivity, offset)

        kwds["set_connectivity"] = False
        super(Unstructured, self).__init__(*args, **kwds)

    def _set_connectivity(self, connectivity, offset):
        self._connectivity = np.array(connectivity, dtype=int)
        self._offset = np.array(offset, dtype=int)
        self._connectivity.shape = self._connectivity.size
        self._offset.shape = self._offset.size
        self._cell_count = self._offset.size


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
