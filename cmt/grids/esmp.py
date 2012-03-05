#! /bin/env python
"""
Examples
========

>>> ESMP.ESMP_Initialize()

>>> g = EsmpStructured ([0, 1, 2, 0, 1, 2], [0, 0, 0, 1, 1, 1], (3, 2))
>>> g = EsmpRectilinear ([0, 1, 2], [0, 1])
>>> g = EsmpUniformRectilinear ([3, 2], [1., 1.], [0., 0.])

Uniform Rectilinear Field
-------------------------

Create a field on a grid that looks like this,

::

    (0) --- (1) --- (2)
     |       |       |
     |   0   |   1   |
     |       |       |
    (3) --- (4) --- (5)

Create the field,

    >>> g = EsmpRasterField ((3,2), (2,1), (0, 0))
    >>> g.get_cell_count ()
    2
    >>> g.get_point_count ()
    6

Add some data at the points of our grid.

    >>> data = np.arange (6)
    >>> g.add_field ('var0', data, centering='point')
    >>> f = g.get_field ('var0')
    >>> f
    array([ 0.,  1.,  2.,  3.,  4.,  5.])
    >>> print f.dtype
    float64

The data can be given either as a 1D array or with the same shape
as the point grid. In either case, though, it will be flattened.

    >>> data = np.arange (6)
    >>> data.shape = (2, 3)
    >>> g.add_field ('var0', data, centering='point')
    >>> f = g.get_field ('var0')
    >>> f
    array([ 0.,  1.,  2.,  3.,  4.,  5.])

If the size or shape doesn't match, it's an error.

    >>> data = np.arange (2)
    >>> g.add_field ('bad var', data, centering='point')
    Traceback (most recent call last):
        ...
    DimensionError: 2 != 6

    >>> data = np.ones ((3, 2))
    >>> g.add_field ('bad var', data, centering='point')
    Traceback (most recent call last):
        ...
    DimensionError: (3, 2) != (2, 3)

Map between two fields
----------------------

    >>> src = EsmpRasterField ((3,3), (1,1), (0, 0))
    >>> data = np.arange (src.get_cell_count (), dtype=np.float64)
    >>> src.add_field ('src', data, centering='zonal')

    >>> dst = EsmpRasterField ((4,4), (.5,.5), (0, 0))
    >>> data = np.empty (dst.get_cell_count (), dtype=np.float64)
    >>> dst.add_field ('dst', data, centering='zonal')

    >>> run_regridding (src.as_esmp ('src'), dst.as_esmp ('dst'))

    >>> ESMP.ESMP_Finalize()
"""

import numpy as np

from cmt.grids.raster import UniformRectilinear
from cmt.grids.rectilinear import Rectilinear
from cmt.grids.structured import Structured
from cmt.grids.unstructured import Unstructured
from cmt.grids.igrid import IGrid, IField, DimensionError,CenteringValueError, centering_choices
import ESMP

class EsmpGrid (IGrid):
    #def __init__ (self, x, y, shape, indexing='xy'):
    def __init__ (self):
        #super (EsmpGrid, self).__init__ (x, y, shape, indexing=indexing)

        shape = self.get_shape ()
        #print shape

        #self._mesh = ESMP.ESMP_MeshCreate (shape[1], shape[0])
        #self._mesh = ESMP.ESMP_MeshCreate (shape[0], shape[1])
        self._mesh = ESMP.ESMP_MeshCreate (2, 2)

        self._mesh_add_nodes ()
        self._mesh_add_elements ()

        super (EsmpGrid, self).__init__ ()

    def as_mesh (self):
        return self._mesh

    def _mesh_add_nodes (self):
        node_ids = np.arange (1, self.get_point_count ()+1, dtype=np.int32)
        (x, y) = (self.get_x (), self.get_y ())

        node_coords = np.empty (x.size+y.size, dtype=np.float32)
        (node_coords[0::2], node_coords[1::2]) = (x, y)

        node_owner = np.zeros (self.get_point_count ())

        ESMP.ESMP_MeshAddNodes (self._mesh, self.get_point_count (), node_ids, node_coords, node_owner)

    def _mesh_add_elements (self):
        cell_ids = np.arange (1, self.get_cell_count ()+1, dtype=np.int32)
        cell_types = (np.zeros (self.get_cell_count (), dtype=np.int32) +
                      ESMP.ESMP_MESHELEMTYPE_QUAD)
        cell_conn = np.array (self.get_connectivity (), dtype=np.int32)+1

        ESMP.ESMP_MeshAddElements (self._mesh, self.get_cell_count (), cell_ids, cell_types, cell_conn)

class EsmpStructured (Structured, EsmpGrid):
    name = 'ESMPStructured'

class EsmpRectilinear (Rectilinear, EsmpGrid):
    name = 'ESMPRectilinear'

class EsmpUniformRectilinear (UniformRectilinear, EsmpStructured):
    name = 'ESMPUniformRectilinear'

#class EsmpField (EsmpGrid, IField):
class EsmpField (IField):
    def __init__ (self, *args, **kwargs):
        super (EsmpField, self).__init__ (*args, **kwargs) 
        self._fields = {}

    def add_field (self, field_name, val, centering='zonal'):

        if centering not in centering_choices:
            raise CenteringValueError (centering)

        if centering=='zonal' and val.size != self.get_cell_count ():
            raise DimensionError (val.size, self.get_cell_count ())
        elif centering!='zonal' and val.size != self.get_point_count ():
            raise DimensionError (val.size, self.get_point_count ())

        if centering=='zonal':
            meshloc=ESMP.ESMP_MESHLOC_ELEMENT
        else:
            meshloc=ESMP.ESMP_MESHLOC_NODE

        field = ESMP.ESMP_FieldCreate (self._mesh, field_name, meshloc=meshloc)
        field_ptr = ESMP.ESMP_FieldGetPtr(field, 0)
        #field_ptr.data = val.data
        field_ptr.flat = val.flat

        self._fields[field_name] = field

    def get_field (self, field_name):
        field = self._fields[field_name]
        return ESMP.ESMP_FieldGetPtr(field, 0)

    def as_esmp (self, field_name):
        return self._fields[field_name]

class EsmpStructuredField (EsmpStructured, EsmpField):
    def add_field (self, field_name, val, centering='zonal'):
        if centering=='zonal':
            if val.ndim > 1 and np.any (val.shape != self.get_shape ()-1):
                raise DimensionError (val.shape, self.get_shape ()-1)
        elif centering!='zonal':
            if val.ndim > 1 and np.any (val.shape != self.get_shape ()):
                raise DimensionError (val.shape, self.get_shape ())
        try:
            super (EsmpStructuredField, self).add_field (field_name, val, centering=centering)
        except DimensionError, CenteringValueError:
            raise

#class EsmpStructuredField (EsmpRectilinear, EsmpField):
#    pass
class EsmpRectilinearField (EsmpRectilinear, EsmpStructuredField):
    pass
#class EsmpRasterField (EsmpUniformRectilinear, EsmpGrid, EsmpField):

class EsmpRasterField (EsmpUniformRectilinear, EsmpRectilinearField):
    pass

def run_regridding(srcfield, dstfield):
    '''
    PRECONDITIONS: Two ESMP_Fields have been created and a regridding operation 
                   is desired from 'srcfield' to 'dstfield'.
    POSTCONDITIONS: An ESMP regridding operation has set the data on 'dstfield'.
    '''
    print 'Running an ESMF regridding operation. . .'

    # call the regridding functions
    routehandle = ESMP.ESMP_FieldRegridStore(srcfield, dstfield,
                                             ESMP.ESMP_REGRIDMETHOD_CONSERVE,
                                             ESMP.ESMP_UNMAPPEDACTION_ERROR)
    ESMP.ESMP_FieldRegrid(srcfield, dstfield, routehandle)
    ESMP.ESMP_FieldRegridRelease(routehandle)

    return dstfield

if __name__ == '__main__':
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)

