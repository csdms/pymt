#! /bin/env python
"""
Examples
========

**Rectilinear**

Create a rectilinear grid that is 2x3::

    (0) --- (1) --- (2)
     |       |       |
     |       |       |
     |  [0]  |  [1]  |
     |       |       |
     |       |       |
    (3) --- (4) --- (5)

Numbers in parens are node IDs, and numbers in square brackets are
cell IDs.

>>> g = RectilinearMap ([0, 2], [0, 1, 2])
>>> g.get_x ()
array([ 0.,  1.,  2.,  0.,  1.,  2.])
>>> g.get_y ()
array([ 0.,  0.,  0.,  2.,  2.,  2.])

Node 1 is shared by both cell 0, and 1; node 5 only is part of cell 1.

>>> g.get_shared_cells (1)
[0, 1]
>>> g.get_shared_cells (5)
[1]

Point (.5, 1.) is contained only within cell 0.

>>> g.is_in_cell (.5, 1., 0)
True
>>> g.is_in_cell (.5, 1., 1)
False

Point (1., 1.) is on a border and so is contained by both cells.

>>> g.is_in_cell (1, 1., 0)
True
>>> g.is_in_cell (1, 1., 1)
True

"""

from pymt.grids import (
    Rectilinear,
    Structured,
    UniformRectilinear,
    Unstructured,
    UnstructuredPoints,
)
from shapely.geometry import Point, asLineString, asPoint, asPolygon


class UnstructuredMap(Unstructured):
    name = "Unstructured"

    def __init__(self, *args, **kwargs):
        super(UnstructuredMap, self).__init__(*args, **kwargs)

        self._point = {}
        last_offset = 0
        for (cell_id, offset) in enumerate(self._offset):
            cell = self._connectivity[last_offset:offset]
            last_offset = offset

            for point_id in cell:
                try:
                    self._point[point_id].append(cell_id)
                except KeyError:
                    self._point[point_id] = [cell_id]

        (point_x, point_y) = (self.get_x(), self.get_y())
        self._polys = []
        last_offset = 0
        for (cell_id, offset) in enumerate(self._offset):
            cell = self._connectivity[last_offset:offset]
            last_offset = offset

            (x, y) = (point_x.take(cell), point_y.take(cell))
            if len(x) > 2:
                self._polys.append(asPolygon(zip(x, y)))
            elif len(x) == 2:
                self._polys.append(asLineString(zip(x, y)))
            else:
                self._polys.append(asPoint(zip(x, y)))

    def get_shared_cells(self, point_id):
        """
        Parameters
        ----------
        point_id: int
            ID of a point in the grid.

        Returns
        -------
        ndarray of int
            Indices to cells that share a given node.
        """
        return self._point[point_id]

    def is_in_cell(self, x, y, cell_id):
        """ Check if a point is in a cell.

        Parameters
        ----------
        x: float
            x-coordinate of point to check.
        y: float
            y-coordinate of point to check.
        cell_id: int
            ID of the cell in the grid.

        Returns
        -------
        bool
            True if the point (x, y) is contained in the cell.
        """
        pt = Point((x, y))
        return self._polys[cell_id].contains(pt) or self._polys[cell_id].touches(pt)


class UnstructuredPointsMap(UnstructuredPoints):
    name = "UnstructuredPoints"

    def get_shared_cells(self, point_id):  # pylint: disable=no-self-use
        return []

    def is_in_cell(self, x, y, cell_id):  # pylint: disable=no-self-use
        return False


class StructuredMap(Structured, UnstructuredMap):
    name = "Structured"


class RectilinearMap(Rectilinear, UnstructuredMap):
    name = "Rectilinear"


class UniformRectilinearMap(UniformRectilinear, UnstructuredMap):
    name = "UniformRectilinear"


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
