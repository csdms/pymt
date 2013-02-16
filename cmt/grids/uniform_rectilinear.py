#! /bin/env python

import numpy as np
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
from shapely.geometry import asPoint, asLineString, asPolygon

class IGrid (object):
    def get_x (self):
        pass
    def get_y (self):
        pass
    def get_connectivity (self):
        pass
    def get_offset (self):
        pass

class IField (IGrid):
    def get_field (self, field_name):
        pass

class UniformRectilinear (IGrid):
    def __init__ (self, shape, spacing, origin, units='-'):
        assert (len (shape) == len (spacing) == len (origin))

        self._shape = np.array (shape, dtype=np.int64)
        self._spacing = np.array (spacing, dtype=np.float64)
        self._origin = np.array (origin, dtype=np.float64)

        xi = []
        for (nx, dx) in zip (shape, spacing):
            xi.append (np.arange (nx, dtype=np.float64)*dx)
        XI = meshgrid.meshgrid (*xi)
        for (x, spacing) in zip (XI, self._spacing):
            x.shape = np.prod (self._shape)
            x[:] -= dx*.5

        point_ids = np.arange (np.prod (self._shape+1), dtype=np.int64)
        if len (shape)==2:
            point_ids.shape = (1, self._shape[0], self._shape[1])
        else:
            point_ids.shape = self._shape

        for i in [0, 1]:
            c_ul = point_ids[i,:-1,:-1].flatten ()
            c_ur = point_ids[i,:-1,1:].flatten ()
            c_lr = point_ids[i,1:,1:].flatten ()
            c_ll = point_ids[i,1:,:-1].flatten ()

        self._connectivity = zip (c_ur, c_ul, c_ll, c_lr)
        self._offset = np.arange (1, shape[0]*shape[1]+1, dtype=np.int32)*4

        for i in (range (0,ni-1), range (1,ni)):
            for j in (range (0,nj-1), range (1,nj)):
                for k in (range (0,nk-1), range (1,nk)):
                    ids = meshgrid.meshgrid (i,j,k, indexing='ij')
                    c = point_ids[i,j,k].flatten ()

                    c_ur = point_ids[i,:-1,1:].flatten ()
                    c_lr = point_ids[i,1:,1:].flatten ()
                    c_ll = point_ids[i,1:,:-1].flatten ()


                    c_ul = point_ids[i,:-1,:-1].flatten ()
                    c_ur = point_ids[i,:-1,1:].flatten ()
                    c_lr = point_ids[i,1:,1:].flatten ()
                    c_ll = point_ids[i,1:,:-1].flatten ()

        self._connectivity = zip (c_ur, c_ul, c_ll, c_lr)
        self._offset = np.arange (1, shape[0]*shape[1]+1, dtype=np.int32)*4

        if swap:
            (y, x) = np.meshgrid (np.arange (shape[1]+1, dtype=np.float)*spacing[1],
                                  np.arange (shape[0]+1, dtype=np.float)*spacing[0])
        else:
            (x, y) = np.meshgrid (np.arange (shape[1]+1, dtype=np.float)*spacing[1],
                                  np.arange (shape[0]+1, dtype=np.float)*spacing[0])
        self._x = x.flatten () - spacing[1]*.5
        self._y = y.flatten () - spacing[0]*.5
        self._z = np.zeros (self._y.size)

        c_ul = np.arange (shape[0]*shape[1], dtype=np.int32)
        c_ul = c_ul + c_ul/shape[1]
        c_ur = c_ul + 1
        c_ll = c_ul + shape[1]+1
        c_lr = c_ul + shape[1]+1 + 1

        self._connectivity = zip (c_ur, c_ul, c_ll, c_lr)
        self._offset = np.arange (1, shape[0]*shape[1]+1, dtype=np.int32)*4

        #self._n_cells = len (self._connectivity)

        self._point = {}
        for (cell_id, cell) in zip (range (len (self._offset)),
                                    self._connectivity):
            for point_id in cell:
                try:
                    self._point[point_id].append (cell_id)
                except KeyError:
                    self._point[point_id] = [cell_id]

        self._polys = [asPolygon (zip (self._x.take (c), self._y.take (c))) for c in self._connectivity]

        self._point_values = {}
        self._cell_values = {}
    def get_shape (self):
        return self._shape
    def get_spacing (self):
        return self._spacing
    def get_origin (self):
        return self._origin
    def get_whole_extent (self):
        return (np.array ([self._x[0], self._x[-1]]),
                np.array ([self._y[0], self._y[-1]]),
                np.zeros (2))
    def cell_count (self):
        return len (self._connectivity)
    def point_count (self):
        return len (self._x)
    def get_connectivity (self):
        try:
            #print 'Get Rectilinear connectivity...'
            c = np.array ([], dtype=np.int32)
            for i in self._connectivity:
                c = np.hstack ([c, i])
            #print 'Got Rectilinear connectivity.'
        except Exception as e:
            print 'ERROR: %s' % e
        return c

    def get_shared_cells (self, point_id):
        return self._point[point_id]

    def is_in_cell (self, x, y, cell_id):
        #return pnpoly (x, y, self.get_cell_xy (cell_id))==1
        pt = Point ((x,y))
        return self._polys[cell_id].contains (pt) or self._polys[cell_id].touches (pt)

    def partition_shape (self, shape):
        rows = np.array ([np.round (1.*self._shape[0]/shape[0])]*shape[0], dtype=np.int32)
        cols = np.array ([np.round (1.*self._shape[1]/shape[1])]*shape[1], dtype=np.int32)
        rows[-1] += (self._shape[0] - rows.sum ())
        cols[-1] += (self._shape[1] - cols.sum ())
        (n, m) = np.meshgrid (cols, rows)

        return (m, n)

    def partition (self, shape):
        #rows = np.array ([np.round (1.*self._shape[0]/shape[0])]*shape[0], dtype=np.int32)
        #cols = np.array ([np.round (1.*self._shape[1]/shape[1])]*shape[1], dtype=np.int32)
        #rows[-1] += (self._shape[0] - rows.sum ())
        #cols[-1] += (self._shape[1] - cols.sum ())
        #(n, m) = np.meshgrid (cols, rows)

        (m, n) = self.partition_shape (shape)
        shapes = zip (m.flatten (), n.flatten ())

        (y0, x0) = ((n.cumsum (axis=1)-n)*self._spacing[1], (m.cumsum (axis=0)-m)*self._spacing[0])
        origins = zip (y0.flatten (), x0.flatten ())

        grids = []
        for (shape, origin) in zip (shapes, origins):
            grids.append (VTKGridUniformRectilinear (shape, self._spacing, origin))

        return grids

    def name (self):
        return 'UniformRectilinear'
    def get_x_coordinates (self):
        return self._x[0:self._shape[1]+1]
    def get_y_coordinates (self):
        return self._y[0::self._shape[1]+1]
    def get_z_coordinates (self):
        return self._z[0]
    def get_grid_coordinates (self):
        return (self.get_x_coordinates (), self.get_y_coordinates (),
                self.get_z_coordinates ())
from matplotlib.nxutils import pnpoly

class VTKGrid (IGrid):
    """

Define a grid that consists of two trianges that share two points.

::

       (2) - (3)
      /   \  /
    (0) - (1)

Create the grid,

    >>> g = VTKGrid ([0, 2, 1, 3], [0, 0, 1, 1], [0, 2, 1, 2, 3, 1], [3, 6])

    >>> x = g.get_x ()
    >>> type (x)
    <type 'numpy.ndarray'>
    >>> x.dtype
    dtype('float64')
    >>> print x
    [ 0. 2. 1. 3.]

    >>> y = g.get_y ()
    >>> type (y)
    <type 'numpy.ndarray'>
    >>> y.dtype
    dtype('float64')
    >>> print y
    [ 0. 0. 1. 1.]

    >>> c = g.get_connectivity ()
    >>> type (c)
    <type 'numpy.ndarray'>
    >>> c.dtype
    dtype('int32')
    >>> print c
    [0 2 1 2 3 1]

    >>> o = g.get_offset ()
    >>> type (o)
    <type 'numpy.ndarray'>
    >>> o.dtype
    dtype('int32')
    >>> print o
    [3 6]

    >>> g.get_shared_cells (0)
    [0]
    >>> g.get_shared_cells (1)
    [0, 1]
    >>> g.get_shared_cells (2)
    [0, 1]
    >>> g.get_shared_cells (3)
    [1]

    >>> [g.is_in_cell (.5, .5, i) for i in range (2)]
    [True, False]
    >>> [g.is_in_cell (2, .5, i) for i in range (2)]
    [False, True]
    >>> [g.is_in_cell (2, 0, i) for i in range (2)]
    [True, True]
    """
    def __init__ (self, x, y, connectivity, offset):
        self._x = np.array (x, dtype=np.float).flatten ()
        self._y = np.array (y, dtype=np.float).flatten ()
        self._z = np.zeros (self._y.size, dtype=np.float).flatten ()

        connectivity  = np.array (connectivity, dtype=np.int32)
        self._offset  = np.array (offset, dtype=np.int32)

        c = []
        offset = 0
        for cell_id in range (len (self._offset)):
            c.append (connectivity[offset:self._offset[cell_id]])
            offset = self._offset[cell_id]
        self._connectivity = c

        self._point = {}
        for (cell_id, cell) in zip (range (len (self._offset)),
                                    self._connectivity):
            for point_id in cell:
                try:
                    self._point[point_id].append (cell_id)
                except KeyError:
                    self._point[point_id] = [cell_id]

        #self._polys = [asPolygon (zip (self._x.take (c), self._y.take (c))) for c in self._connectivity]
        self._polys = []
        for c in self._connectivity:
            (x, y) = (self._x.take (c), self._y.take (c))
            if len (x)>2:
                self._polys.append (asPolygon (zip (x, y)))
            elif len (x)==2:
                self._polys.append (asLineString (zip (x, y)))
            else:
                self._polys.append (asPoint (zip (x, y)))


        #offset = 0
        #for cell_id in range (len (self._offset)):
        #    cell = self._connectivity[offset:self._offset[cell_id]]
        #    for point_id in cell:
        #        try:
        #            self._point[point_id].append (cell_id)
        #        except KeyError:
        #            self._point[point_id] = [cell_id]
        #    offset = self._offset[cell_id]

        self._point_values = {}
        self._cell_values = {}

    def point_data (self, name):
        return self._point_values[name]
    def point_data_vars (self):
        return self._point_values.keys ()
    def cell_data (self, name):
        return self._cell_values[name]
    def cell_data_vars (self):
        return self._cell_values.keys ()
    def add_point_data (self, name, data):
        self._point_values[name] = np.array (data)
    def add_cell_data (self, name, data):
        self._cell_values[name] = np.array (data)
    def point_count (self):
        return len (self._x)
    def cell_count (self):
        return len (self._offset)
    def size (self):
        return self._x.size
    def get_x (self):
        return self._x
    def get_y (self):
        return self._y
    def get_z (self):
        return self._z
    def get_coordinates (self):
        return (self._x, self._y, np.zeros (self._x.size))
    def get_connectivity (self):
        c = np.array ([], dtype=np.int32)
        for i in self._connectivity:
            c = np.hstack ([c, i])
        return c
    def get_offset (self):
        return self._offset
    def get_cell_xy (self, i):
        ids = self._connectivity[i]
        x = self._x.take (ids)
        y = self._y.take (ids)
        return zip (x,y)
    def get_shared_cells (self, point_id):
        return self._point[point_id]
    def is_in_cell (self, x, y, cell_id):
        #return pnpoly (x, y, self.get_cell_xy (cell_id))==1
        pt = Point ((x,y))
        return self._polys[cell_id].contains (pt) or self._polys[cell_id].touches (pt)
    def is_point (self, cell_id):
        return len (self._connectivity [cell_id])==1

    def name (self):
        return 'NonUniformMesh'

class VTKGridPoints (VTKGrid):
    """
    >>> g = VTKGridPoints ([1, 2, 3,], [0, 1, -1])
    >>> g.point_count ()
    3
    >>> g.cell_count ()
    0

    >>> x = g.get_x ()
    >>> type (x)
    <type 'numpy.ndarray'>
    >>> x.dtype
    dtype('float64')
    >>> print x
    [ 1. 2. 3.]

    >>> y = g.get_y ()
    >>> type (y)
    <type 'numpy.ndarray'>
    >>> y.dtype
    dtype('float64')
    >>> print y
    [ 0. 1. -1.]

    >>> c = g.get_connectivity ()
    >>> type (c)
    <type 'numpy.ndarray'>
    >>> c.dtype
    dtype('int32')
    >>> print c
    [0 1 2]

    >>> o = g.get_offset ()
    >>> type (o)
    <type 'numpy.ndarray'>
    >>> o.dtype
    dtype('int32')
    >>> print o
    [1 2 3]

    """
    def __init__ (self, x, y):
        try:
            self._x = np.array (x.flatten (), dtype=np.float)
        except AttributeError:
            self._x = np.array (x, dtype=np.float)
        try:
            self._y = np.array (y.flatten (), dtype=np.float)
        except AttributeError:
            self._y = np.array (y, dtype=np.float)

        self._connectivity = np.arange (self._x.size, dtype=np.int32)
        self._offset = np.arange (1, self._x.size+1, dtype=np.int32)

    def point_count (self):
        return len (self._x)
    def cell_count (self):
        return 0
    def get_shared_cells (self, point_id):
        return []
    def name (self):
        return 'XYPoints'

class VTKGridUniformRectilinear (VTKGrid):
    """
    Create a grid that is 2x3. y is the first (slow) dimension,
    x is the second (fast) dimension. The shape of the grid
    is the number of grid cells (not points).

    >>> grid = VTKGridUniformRectilinear ([2, 3], [1, 1])
    >>> print grid.get_x ()
    [-0.5 0.5 1.5 2.5 -0.5 0.5 1.5 2.5 -0.5 0.5 1.5 2.5]
    >>> print grid.get_y ()
    [-0.5 -0.5 -0.5 -0.5 0.5 0.5 0.5 0.5 1.5 1.5 1.5 1.5]
    >>> print grid.get_connectivity ()
    [ 1 0 4 5   2 1 5 6   3 2 6 7   5 4 8 9   6 5 9 10   7 6 10 11]
    >>> print grid.get_offset ()
    [ 4 8 12 16 20 24]

    >>> x = grid.get_x ()
    >>> type (x)
    <type 'numpy.ndarray'>
    >>> x.dtype
    dtype('float64')

    >>> y = grid.get_y ()
    >>> type (y)
    <type 'numpy.ndarray'>
    >>> y.dtype
    dtype('float64')

    >>> c = grid.get_connectivity ()
    >>> type (c)
    <type 'numpy.ndarray'>
    >>> c.dtype
    dtype('int32')

    >>> o = grid.get_offset ()
    >>> type (o)
    <type 'numpy.ndarray'>
    >>> o.dtype
    dtype('int32')

    >>> grid.get_shared_cells (0)
    [0]
    >>> grid.get_shared_cells (11)
    [5]
    >>> grid.get_shared_cells (5)
    [0, 1, 3, 4]

    >>> grid = VTKGridUniformRectilinear ([20, 30], [1, 1])
    >>> (m, n) = grid.partition_shape ((3,4))
    >>> m
    array([[7, 7, 7, 7],
           [7, 7, 7, 7],
           [6, 6, 6, 6]], dtype=int32)
    >>> n
    array([[8, 8, 8, 6],
           [8, 8, 8, 6],
           [8, 8, 8, 6]], dtype=int32)

    >>> (m, n) = grid.partition_shape ((2,5))
    >>> m
    array([[10, 10, 10, 10, 10],
           [10, 10, 10, 10, 10]], dtype=int32)
    >>> n
    array([[6, 6, 6, 6, 6],
           [6, 6, 6, 6, 6]], dtype=int32)

    >>> grids = grid.partition ((3,4))
    >>> for grid in grids: print grid._shape, grid._origin

    """

    def __init__ (self, shape, spacing, origin=(0, 0), at_nodes=False, swap=False):
        if at_nodes:
            shape[1] -= 1
            shape[0] -= 1

        self._shape = shape
        self._spacing = spacing
        self._origin = origin

        if swap:
            (y, x) = np.meshgrid (np.arange (shape[1]+1, dtype=np.float)*spacing[1],
                                  np.arange (shape[0]+1, dtype=np.float)*spacing[0])
        else:
            (x, y) = np.meshgrid (np.arange (shape[1]+1, dtype=np.float)*spacing[1],
                                  np.arange (shape[0]+1, dtype=np.float)*spacing[0])
        self._x = x.flatten () - spacing[1]*.5
        self._y = y.flatten () - spacing[0]*.5
        self._z = np.zeros (self._y.size)

        c_ul = np.arange (shape[0]*shape[1], dtype=np.int32)
        c_ul = c_ul + c_ul/shape[1]
        c_ur = c_ul + 1
        c_ll = c_ul + shape[1]+1
        c_lr = c_ul + shape[1]+1 + 1

        self._connectivity = zip (c_ur, c_ul, c_ll, c_lr)
        self._offset = np.arange (1, shape[0]*shape[1]+1, dtype=np.int32)*4

        #self._n_cells = len (self._connectivity)

        self._point = {}
        for (cell_id, cell) in zip (range (len (self._offset)),
                                    self._connectivity):
            for point_id in cell:
                try:
                    self._point[point_id].append (cell_id)
                except KeyError:
                    self._point[point_id] = [cell_id]

        self._polys = [asPolygon (zip (self._x.take (c), self._y.take (c))) for c in self._connectivity]

        self._point_values = {}
        self._cell_values = {}
    def get_shape (self):
        return self._shape
    def get_spacing (self):
        return self._spacing
    def get_origin (self):
        return self._origin
    def get_whole_extent (self):
        return (np.array ([self._x[0], self._x[-1]]),
                np.array ([self._y[0], self._y[-1]]),
                np.zeros (2))
    def cell_count (self):
        return len (self._connectivity)
    def point_count (self):
        return len (self._x)
    def get_connectivity (self):
        try:
            #print 'Get Rectilinear connectivity...'
            c = np.array ([], dtype=np.int32)
            for i in self._connectivity:
                c = np.hstack ([c, i])
            #print 'Got Rectilinear connectivity.'
        except Exception as e:
            print 'ERROR: %s' % e
        return c

    def get_shared_cells (self, point_id):
        return self._point[point_id]

    def is_in_cell (self, x, y, cell_id):
        #return pnpoly (x, y, self.get_cell_xy (cell_id))==1
        pt = Point ((x,y))
        return self._polys[cell_id].contains (pt) or self._polys[cell_id].touches (pt)

    def partition_shape (self, shape):
        rows = np.array ([np.round (1.*self._shape[0]/shape[0])]*shape[0], dtype=np.int32)
        cols = np.array ([np.round (1.*self._shape[1]/shape[1])]*shape[1], dtype=np.int32)
        rows[-1] += (self._shape[0] - rows.sum ())
        cols[-1] += (self._shape[1] - cols.sum ())
        (n, m) = np.meshgrid (cols, rows)

        return (m, n)

    def partition (self, shape):
        #rows = np.array ([np.round (1.*self._shape[0]/shape[0])]*shape[0], dtype=np.int32)
        #cols = np.array ([np.round (1.*self._shape[1]/shape[1])]*shape[1], dtype=np.int32)
        #rows[-1] += (self._shape[0] - rows.sum ())
        #cols[-1] += (self._shape[1] - cols.sum ())
        #(n, m) = np.meshgrid (cols, rows)

        (m, n) = self.partition_shape (shape)
        shapes = zip (m.flatten (), n.flatten ())

        (y0, x0) = ((n.cumsum (axis=1)-n)*self._spacing[1], (m.cumsum (axis=0)-m)*self._spacing[0])
        origins = zip (y0.flatten (), x0.flatten ())

        grids = []
        for (shape, origin) in zip (shapes, origins):
            grids.append (VTKGridUniformRectilinear (shape, self._spacing, origin))

        return grids

    def name (self):
        return 'UniformRectilinear'
    def get_x_coordinates (self):
        return self._x[0:self._shape[1]+1]
    def get_y_coordinates (self):
        return self._y[0::self._shape[1]+1]
    def get_z_coordinates (self):
        return self._z[0]
    def get_grid_coordinates (self):
        return (self.get_x_coordinates (), self.get_y_coordinates (),
                self.get_z_coordinates ())

class VTKGridRectilinear (VTKGrid):
    def __init__ (self, x, y):
        (self._x, self._y) = np.meshgrid (x, y)

        self._n_points = self._x.size
        self._n_cells = (self._x.shape[0]-1)*(self._x.shape[1]-1)
        self._shape = (self._x.shape[0]-1, self._x.shape[1]-1)

        self._x = self._x.flatten ()
        self._y = self._y.flatten ()
        self._z = np.zeros (self._y.size)

        shape = (self._shape[0], self._shape[1])
        c_ul = np.arange (self._n_cells, dtype=np.int32)
        c_ul = c_ul + c_ul/shape[1]
        c_ur = c_ul + 1
        c_ll = c_ul + shape[1]+1
        c_lr = c_ul + shape[1]+1 + 1

        self._connectivity = zip (c_ur, c_ul, c_ll, c_lr)
        self._offset = np.arange (1, self._n_cells+1, dtype=np.int32)*4

        self._point = {}
        for (cell_id, cell) in zip (range (len (self._offset)),
                                    self._connectivity):
            for point_id in cell:
                try:
                    self._point[point_id].append (cell_id)
                except KeyError:
                    self._point[point_id] = [cell_id]

        self._polys = [asPolygon (zip (self._x.take (c), self._y.take (c))) for c in self._connectivity]

        self._point_values = {}
        self._cell_values = {}
    def get_shape (self):
        return self._shape
    def get_x_coordinates (self):
        return self._x[0:self._shape[1]+1]
    def get_y_coordinates (self):
        return self._y[0::self._shape[1]+1]
    def get_z_coordinates (self):
        return self._z[0]
    def get_grid_coordinates (self):
        return (self.get_x_coordinates (), self.get_y_coordinates (),
                self.get_z_coordinates ())

class VTKGridStructured (VTKGrid):
    def __init__ (self, x, y, extent):
        self._x = np.array (x).flatten ()
        self._y = np.array (y).flatten ()
        self._z = np.zeros (self._y.size)

        self._n_points = self._x.size
        self._n_cells = (extent[0]-1)*(extent[1]-1)
        self._shape = (extent[0]-1, extent[1]-1)

        shape = (self._shape[0], self._shape[1])
        c_ul = np.arange (self._n_cells, dtype=np.int32)
        c_ul = c_ul + c_ul/shape[1]
        c_ur = c_ul + 1
        c_ll = c_ul + shape[1]+1
        c_lr = c_ul + shape[1]+1 + 1

        self._connectivity = zip (c_ur, c_ul, c_ll, c_lr)
        self._offset = np.arange (1, self._n_cells+1, dtype=np.int32)*4

        self._point = {}
        for (cell_id, cell) in zip (range (len (self._offset)),
                                    self._connectivity):
            for point_id in cell:
                try:
                    self._point[point_id].append (cell_id)
                except KeyError:
                    self._point[point_id] = [cell_id]

        self._polys = [asPolygon (zip (self._x.take (c), self._y.take (c))) for c in self._connectivity]

        self._point_values = {}
        self._cell_values = {}
    def get_shape (self):
        return self._shape

class IElementSet (object):
    def getElementCount (self):
        pass
    def getVertexCount (self, i):
        pass
    def getXCoordinate (self, i, j):
        pass
    def getYCoordinate (self, i, j):
        pass
    def getZCoordinate (self, i, j):
        pass

class ElementSet (IElementSet):
    def __init__ (self, x, y, z):
        self._x = x
        self._y = y
        self._z = z

    def getElementCount (self):
        return len (self._x)
    def getVertexCount (self, i):
        return len (self._x[i])
    def getXCoordinate (self, i, j):
        return self._x[i][j]
    def getYCoordinate (self, i, j):
        return self._y[i][j]
    def getZCoordinate (self, i, j):
        return self._z[i][j]

class OpenMIGrid (VTKGrid):
    """
    >>> x = [[0, 5, 10], [10, 5, 20]]
    >>> y = [[0, 5, 0], [0, 5, 10]]
    >>> z = [[0, 0, 0], [0, 0, 0]]
    >>> element_set = ElementSet (x, y, z)
    >>> g = OpenMIGrid (element_set)

    x, y, and z are 1D numpy arrays of floats

    >>> x = g.get_x ()
    >>> type (x)
    <type 'numpy.ndarray'>
    >>> x.dtype
    dtype('float64')
    >>> print x
    [ 0. 5. 10. 10. 5. 20.]

    >>> y = g.get_y ()
    >>> type (y)
    <type 'numpy.ndarray'>
    >>> y.dtype
    dtype('float64')
    >>> print y
    [ 0. 5. 0. 0. 5. 10.]

    connectivity and offset are 1D numpy arrays of ints

    >>> c = g.get_connectivity ()
    >>> type (c)
    <type 'numpy.ndarray'>
    >>> c.dtype
    dtype('int32')
    >>> print c
    [0 1 2 3 4 5]

    >>> o = g.get_offset ()
    >>> type (o)
    <type 'numpy.ndarray'>
    >>> o.dtype
    dtype('int32')
    >>> print o
    [3 6]
    """
    def __init__ (self, element_set):
        self._connectivity = []
        offsets = []
        x = []
        y = []
        z = []
        n_elements = element_set.getElementCount ()
        for i in range (n_elements):
            n_vertices = element_set.getVertexCount (i)
            for j in range (n_vertices):
                x.append (element_set.getXCoordinate (i, j))
                y.append (element_set.getYCoordinate (i, j))
                z.append (element_set.getZCoordinate (i, j))

            try:
                c = np.arange (n_vertices, dtype=np.int32)+offset
            except NameError:
                c = np.arange (n_vertices, dtype=np.int32)
                offset = 0
            self._connectivity.append (c)
            offset += n_vertices

            offsets.append (offset)

        self._offset = np.array (offsets, dtype=np.int32)
        self._x = np.array (x, dtype=np.float)
        self._y = np.array (y, dtype=np.float)
        self._z = np.array (z, dtype=np.float)

    def get_connectivity (self):
        c = np.array ([], dtype=np.int32)
        for i in self._connectivity:
            c = np.hstack ([c, i])
        return c

if __name__ == '__main__':
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)


