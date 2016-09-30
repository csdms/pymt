#! /bin/env python
"""
Examples
========

Point-to-point Mapping
----------------------

>>> import numpy as np
>>> from pymt.grids.map import RectilinearMap as Rectilinear

>>> src = Rectilinear([0, 1, 2], [0, 2])
>>> dst = Rectilinear([.5, 1.5, 2.5], [.25, 1.25])

>>> src.get_x()
array([ 0.,  2.,  0.,  2.,  0.,  2.])

>>> src.get_y()
array([ 0.,  0.,  1.,  1.,  2.,  2.])

>>> dst.get_x()
array([ 0.25,  1.25,  0.25,  1.25,  0.25,  1.25])
>>> dst.get_y()
array([ 0.5,  0.5,  1.5,  1.5,  2.5,  2.5])

>>> src_vals = np.arange(src.get_point_count(), dtype=np.float64)

Map the source values on the source points to the destination grid
using nearest neighbor.

>>> from pymt.mappers import NearestVal

>>> mapper = NearestVal()
>>> mapper.initialize(dst, src)
>>> mapper.run(src_vals)
array([ 0.,  1.,  2.,  3.,  4.,  5.])

>>> mappers = find_mapper(dst, src)
>>> len(mappers)
3
>>> mappers[0].name()
'PointToPoint'

>>> src_vals[2] = -999
>>> dst_vals = np.zeros(dst.get_point_count ()) - 1
>>> mapper.run(src_vals, dst_vals)
array([ 0.,  1., -1.,  3.,  4.,  5.])

Cell-to-point Mapping
---------------------

The source grid looks like,

::

    (0) ------ (1)
     |          |
     |          |
    (2) ------ (3)
     |          |
     |          |
    (4) ------ (5)
     |          |
     |          |
    (7) ------ (7)

>>> from pymt.mappers import CellToPoint
>>> from pymt.grids.map import UniformRectilinearMap as UniformRectilinear
>>> from pymt.grids.map import UnstructuredPointsMap as UnstructuredPoints

>>> (dst_x, dst_y) = (np.array([.45, 1.25, 3.5]), np.array([.75, 2.25, 3.25]))

>>> src = UniformRectilinear((2,4), (2, 1), (0, 0))
>>> dst = UnstructuredPoints(dst_x, dst_y)

>>> src_vals = np.arange(src.get_cell_count(), dtype=np.float64)

>>> mapper = CellToPoint()
>>> mapper.initialize(dst, src)
>>> mapper.run(src_vals, bad_val=-999)
array([   0.,    2., -999.])

>>> src_vals = np.arange(src.get_cell_count(), dtype=np.float64)
>>> src_vals[0] = -9999
>>> dst_vals = np.zeros(dst.get_point_count()) + 100
>>> _ = mapper.run(src_vals, dst_vals)
>>> dst_vals
array([ 100.,    2., -999.])

Point-to-cell Mapping
---------------------

>>> from pymt.mappers.pointtocell import PointToCell
>>> (src_x, src_y) = (np.array ([.45, 1.25, 3.5, .0, 1.]),
...                   np.array ([.75, 2.25, 3.25, .9, 1.1]))

>>> src = UnstructuredPoints(src_x, src_y)
>>> dst = UniformRectilinear((2,4), (2, 1), (0, 0))

>>> src_vals = np.arange(src.get_point_count(), dtype=np.float64)

>>> mapper = PointToCell()
>>> mapper.initialize(dst, src)

>>> mapper.run(src_vals, bad_val=-999)
array([ 1.5,  4. ,  1. ])

>>> mapper.run(src_vals, bad_val=-999, method=np.sum)
array([ 3.,  4.,  1.])

>>> src_vals[0] = -9999
>>> dst_vals = np.zeros(dst.get_cell_count ()) - 1
>>> _ = mapper.run(src_vals, dst_vals)
>>> dst_vals
array([-1.,  4.,  1.])


Point on cell edges
-------------------

>>> (src_x, src_y) = (np.array ([0, .5, 1., 2, 3.5]),
...                   np.array ([1., 1., .0, 3, 3.]))
>>> src = UnstructuredPoints(src_x, src_y)
>>> dst = UniformRectilinear((2,4), (2, 1), (0, 0))

>>> mapper = PointToCell()
>>> mapper.initialize(dst, src)

>>> src_vals = np.arange(src.get_point_count(), dtype=np.float64)
>>> dst_vals = np.zeros(dst.get_cell_count()) - 1
>>> _ = mapper.run(src_vals, dst_vals)
>>> dst_vals
array([ 1. ,  0.5,  3. ])

A big mapper
============

>>> (m, n) = (20, 40)
>>> (src_x, src_y) = np.meshgrid(range(m), range(n))
>>> src = UnstructuredPoints(src_y, src_x)
>>> dst = UniformRectilinear((n + 1, m + 1), (1, 1), (-.5, -.5))

>>> mapper = PointToCell()
>>> mapper.initialize(dst, src)

>>> src_vals = np.arange(src.get_point_count(), dtype=np.float64)
>>> dst_vals = np.zeros(dst.get_cell_count(), dtype=np.float64) - 1
>>> _ = mapper.run(src_vals, dst_vals)

>>> from numpy.testing import assert_array_equal
>>> assert_array_equal(dst_vals, src_vals)
"""

from .pointtopoint import NearestVal
from .celltopoint import CellToPoint
from .pointtocell import PointToCell
from .imapper import IncompatibleGridError


_MAPPERS = [NearestVal, CellToPoint, PointToCell]


def find_mapper(dst_grid, src_grid):
    """Find appropriate mappers to map bewteen two grid-like objects"""
    choices = []
    for cls in _MAPPERS:
        mapper = cls()
        if mapper.test(dst_grid, src_grid):
            choices.append(mapper)

    if len(choices) == 0:
        raise IncompatibleGridError()
    
    return choices
