#! /bin/env python
"""
Examples
========

Point-to-point Mapping
----------------------

>>> import numpy as np
>>> from cmt.grids.map import RectilinearMap as Rectilinear

>>> src = Rectilinear ([0, 1, 2], [0, 2])
>>> dst = Rectilinear ([.5, 1.5, 2.5], [.25, 1.25])

>>> src.get_x ()
array([ 0., 1., 2., 0., 1., 2.])

>>> src.get_y ()
array([ 0., 0., 0., 2., 2., 2.])

>>> dst.get_x ()
array([ 0.5, 1.5, 2.5, 0.5, 1.5, 2.5])
>>> dst.get_y ()
array([ 0.25, 0.25, 0.25, 1.25, 1.25, 1.25])

>>> src_vals = np.arange (src.get_point_count ())

Map the source values on the source points to the destination grid
using nearest neighbor.

>>> from cmt.mappers import NearestVal

>>> mapper = NearestVal ()
>>> mapper.initialize (dst, src)
>>> dst_vals = mapper.run (src_vals)

>>> print dst_vals
[ 0.  1.  2.  3.  4.  5.]

>>> mappers = find_mapper (dst, src)
>>> len (mappers)
3
>>> mappers[0].name ()
'PointToPoint'

>>> src_vals[2] = -999
>>> dst_vals = np.zeros (dst.get_point_count ())-1
>>> dummy = mapper.run (src_vals, dst_vals)
>>> dst_vals
array([ 0.,  1.,  -1.,  3.,  4.,  5.])

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

>>> from cmt.mappers import CellToPoint
>>> from cmt.grids.map import UniformRectilinearMap as UniformRectilinear
>>> from cmt.grids.map import UnstructuredPointsMap as UnstructuredPoints

>>> (dst_x, dst_y) = (np.array ([.45, 1.25, 3.5]), np.array ([.75, 2.25, 3.25]))

>>> src = UniformRectilinear ((2,4), (2, 1), (0, 0))
>>> dst = UnstructuredPoints (dst_x, dst_y)

>>> src_vals = np.arange (src.get_cell_count (), dtype=np.float)

>>> mapper = CellToPoint ()
>>> mapper.initialize (dst, src)
>>> dst_vals = mapper.run (src_vals, bad_val=-999)
>>> print dst_vals
[ 0. 2. -999.]

>>> src_vals = np.arange (src.get_cell_count (), dtype=np.float)
>>> src_vals[0] = -9999
>>> dst_vals = np.zeros (dst.get_point_count ())+100
>>> dummy = mapper.run (src_vals, dst_vals)
>>> print dst_vals
[ 100. 2. -999.]

Point-to-cell Mapping
---------------------

>>> from cmt.mappers import PointToCell
>>> (src_x, src_y) = (np.array ([.45, 1.25, 3.5, .0, 1.]), np.array ([.75, 2.25, 3.25, .9, 1.1]))

>>> src = UnstructuredPoints (src_x, src_y)
>>> dst = UniformRectilinear ((2,4), (2, 1), (0, 0))

>>> src_vals = np.arange (src.get_point_count (), dtype=np.float)

>>> mapper = PointToCell ()
>>> mapper.initialize (dst, src)

>>> dst_vals = mapper.run (src_vals, bad_val=-999)
>>> print dst_vals
[ 1.5 4. 1. ]

[   1.5 4.  -999.  -999.  -999.     1.  -999.     -999. ]

>>> dst_vals = mapper.run (src_vals, bad_val=-999, method=np.sum)
>>> print dst_vals
[ 3. 4. 1.]

[   3. 4. -999. -999. -999.    1. -999.    -999.]

>>> src_vals[0] = -9999
>>> dst_vals = np.zeros (dst.get_cell_count ())-1
>>> dummy = mapper.run (src_vals, dst_vals)
>>> print dst_vals
[-1. 4. 1.]

[-1. 4. -1. -1. -1. 1. -1. -1.]


Point on cell edges
-------------------

>>> (src_x, src_y) = (np.array ([0, .5, 1., 2, 3.5]), np.array ([1., 1., .0, 3, 3.]))
>>> src = UnstructuredPoints (src_x, src_y)
>>> dst = UniformRectilinear ((2,4), (2, 1), (0, 0))

>>> mapper = PointToCell ()
>>> mapper.initialize (dst, src)

>>> src_vals = np.arange (src.get_point_count (), dtype=np.float)
>>> dst_vals = np.zeros (dst.get_cell_count ())-1
>>> dummy = mapper.run (src_vals, dst_vals)
>>> print dst_vals
[ 1. 0.5 3. ]

[ 0.5 1.5 -1. -1. 0.5 1. 3. 4. ]

A big mapper
============

>>> (m, n) = (20, 40)
>>> (src_x, src_y) = np.meshgrid (range (m), range (n))
>>> src = UnstructuredPoints (src_x, src_y)
>>> dst = UniformRectilinear ((m+1,n+1), (1, 1), (-.5, -.5))

>>> mapper = PointToCell ()
>>> mapper.initialize (dst, src)

>>> src_vals = np.arange (src.get_point_count (), dtype=np.float)
>>> dst_vals = np.zeros (dst.get_cell_count (), dtype=np.float)-1
>>> dummy = mapper.run (src_vals, dst_vals)

>>> all (dst_vals==src_vals)
True

"""

from pointtopoint import NearestVal
from celltopoint import CellToPoint
from pointtocell import PointToCell

class MapperError (Exception):
    """Base class for error in this package."""
    pass

class IncompatibleGridError (MapperError):
    """Error to indicate that the source grid cannot be mapped to the destination."""
    def __init__ (self, dst, src):
        self._src = src
        self._dst = dst
    def __str__ (self):
        return 'Unable to map %s to %s' % (self._src, self._dst)

class NoMapperError (MapperError):
    def __init__ (self, dst, src):
        self._src = src
        self._dst = dst
    def __str__ (self):
        return 'No mapper to map %s to %s' % (self._src, self._dst)

#mappers = [NearestVal (), CellToPoint (), PointToCell ()]
mappers = [NearestVal, CellToPoint, PointToCell]

def find_mapper (dst_grid, src_grid):
    """Find appropriate mappers to map bewteen two grid-like objects"""
    choices = []
    for cls in mappers:
        mapper = cls ()
        if mapper.test (dst_grid, src_grid):
            choices.append (mapper)

    if len (choices)==0:
        raise IncompatibleGridError (dst_grid.name, src_grid.name)
    
    return choices

if __name__ == "__main__":
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)

