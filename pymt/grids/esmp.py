#! /bin/env python
"""PyMT interface to ESMPy grids.

**Examples**

Create a grid that looks like this,

::

    (3) --- (4) --- (5)
     |       |       |
     |   0   |   1   |
     |       |       |
    (0) --- (1) --- (2)


>>> import ESMF
>>> mngr = ESMF.Manager()
>>> mngr.local_pet
0
>>> mngr.pet_count
1

Represent this grid as an unstructured grid.

>>> g = EsmpUnstructured([0, 0, 0, 1, 1, 1], [0, 1, 2, 0, 1, 2],
...                      [0, 1, 4, 3, 1, 2, 5, 4], [4, 8], indexing='ij')
>>> g.get_point_count()
6
>>> g.get_cell_count()
2

As a structured grid,

>>> g = EsmpStructured([0, 0, 0, 1, 1, 1], [0, 1, 2, 0, 1, 2], (2, 3),
...                    indexing='ij')
>>> g.get_point_count()
6
>>> g.get_cell_count()
2

As a uniform rectilinear (raster) grid,

>>> g = EsmpUniformRectilinear([2, 3], [1., 1.], [0., 0.])
>>> g.get_point_count()
6
>>> g.get_cell_count()
2

The as_mesh method provides a view of the grid as an ESMP_Mesh.

>>> mesh = g.as_mesh()
>>> mesh.node_count
6
>>> mesh.element_count
2

ESMF elements are the same as the grids cells. Likewise with nodes and points.

>>> g = EsmpRectilinear([0, 1], [0, 1, 2], indexing='ij')
>>> g.as_mesh().element_count == g.get_cell_count()
True
>>> g.as_mesh().node_count == g.get_point_count()
True


**Uniform Rectilinear Field**

Create a field on a grid that looks like this,

::

    (3) --- (4) --- (5)
     |       |       |
     |   0   |   1   |
     |       |       |
    (0) --- (1) --- (2)

Create the field,

>>> g = EsmpRasterField((2, 3), (1, 2), (0, 0), indexing='ij')
>>> g.get_cell_count()
2
>>> g.get_point_count()
6

Add some data at the points of our grid.

>>> data = np.arange(6)
>>> g.add_field('var0', data, centering='point')
>>> f = g.get_field('var0')
>>> f.data
array([ 0.,  1.,  2.,  3.,  4.,  5.])

The data can be given either as a 1D array or with the same shape
as the point grid. In either case, though, it will be flattened.

>>> data = np.arange(6)
>>> data.shape = (2, 3)
>>> g.add_field('var0', data, centering='point')
>>> f = g.get_field('var0')
>>> f.data
array([ 0.,  1.,  2.,  3.,  4.,  5.])

If the size or shape doesn't match, it's an error.

>>> data = np.arange(2)
>>> g.add_field('bad var', data, centering='point') # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
    ...
DimensionError: 2 != 6

>>> data = np.ones((3, 2))
>>> g.add_field ('bad var', data, centering='point') # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
    ...
DimensionError: (3, 2) != (2, 3)


**Map between two fields**

>>> from pymt.grids.raster import UniformRectilinear
>>> from pymt.grids.rectilinear import Rectilinear

>>> src = EsmpRasterField((3,3), (1,1), (0, 0), indexing='ij')
>>> data = np.arange(src.get_cell_count(), dtype=np.float64)
>>> src.add_field('srcfield', data, centering='zonal')
>>> src.get_point_count()
9
>>> src.get_cell_count()
4
>>> src.get_x()
array([ 0.,  1.,  2.,  0.,  1.,  2.,  0.,  1.,  2.])
>>> src.get_y()
array([ 0.,  0.,  0.,  1.,  1.,  1.,  2.,  2.,  2.])
>>> src.get_connectivity() + 1
array([1, 2, 5, 4, 2, 3, 6, 5, 4, 5, 8, 7, 5, 6, 9, 8])

>>> dst = EsmpRectilinearField([0., .5, 1.5, 2.], [0., .5, 1.5, 2.])
>>> data = np.empty(dst.get_cell_count(), dtype=np.float64)
>>> dst.add_field('dstfield', data, centering='zonal')
>>> dst.get_point_count()
16
>>> dst.get_cell_count()
9
>>> dst.get_x()
array([ 0. ,  0.5,  1.5,  2. ,  0. ,  0.5,  1.5,  2. ,  0. ,  0.5,  1.5,
        2. ,  0. ,  0.5,  1.5,  2. ])
>>> dst.get_y()
array([ 0. ,  0. ,  0. ,  0. ,  0.5,  0.5,  0.5,  0.5,  1.5,  1.5,  1.5,
        1.5,  2. ,  2. ,  2. ,  2. ])
>>> dst.get_connectivity() + 1
array([ 1,  2,  6,  5,  2,  3,  7,  6,  3,  4,  8,  7,  5,  6, 10,  9,  6,
        7, 11, 10,  7,  8, 12, 11,  9, 10, 14, 13, 10, 11, 15, 14, 11, 12,
       16, 15])

>>> src_field = src.as_esmp('srcfield')
>>> dst_field = dst.as_esmp('dstfield')
>>> src.as_mesh().element_count
4
>>> src.as_mesh().node_count
9
>>> dst.as_mesh().element_count
9
>>> dst.as_mesh().node_count
16

>>> f = run_regridding(src_field, dst_field)
>>> f.data
array([ 0. ,  0.5,  1. ,  1. ,  1.5,  2. ,  2. ,  2.5,  3. ])

**A bigger grid**

>>> (M, N) = (300, 300)
>>> src = EsmpRasterField((M, N), (1, 1), (0, 0))

**Map values on cells**

>>> (X, Y) = np.meshgrid(np.arange (0.5, 299.5, 1.),
...                      np.arange (0.5, 299.5, 1.))
>>> data = np.sin(np.sqrt(X ** 2 + Y ** 2) * np.pi / M)
>>> src.add_field('srcfield', data, centering='zonal')

>>> dst = EsmpRasterField((M * 2 - 1, N * 2 - 1), (1. / 2, 1. / 2), (0, 0))
>>> data = np.empty(dst.get_cell_count(), dtype=np.float64)
>>> dst.add_field('dstfield', data, centering='zonal')

>>> src_field = src.as_esmp('srcfield')
>>> dst_field = dst.as_esmp('dstfield')

>>> f = run_regridding(src_field, dst_field)

>>> (X, Y) = np.meshgrid(np.arange (0.5, 299.5, .5),
...                      np.arange (0.5, 299.5, .5))
>>> exact = np.sin(np.sqrt(X ** 2 + Y ** 2) * np.pi / M)
>>> np.sum(np.abs(exact.flat - f.data))/(M * N * 4.) < 1e-2
True

**Map values on points**

>>> (X, Y) = np.meshgrid(np.arange(0.5, 300.5, 1.),
...                      np.arange(0.5, 300.5, 1.))
>>> data = np.sin(np.sqrt(X ** 2 + Y ** 2) * np.pi / M)
>>> src.add_field('srcfield_at_points', data, centering='point')

>>> data = np.empty(dst.get_point_count(), dtype=np.float64)
>>> dst.add_field('dstfield_at_points', data, centering='point')

>>> src_field = src.as_esmp('srcfield_at_points')
>>> dst_field = dst.as_esmp('dstfield_at_points')

>>> f = run_regridding(src_field, dst_field,
...                    method=ESMF.RegridMethod.BILINEAR)

>>> (X, Y) = np.meshgrid(np.arange(0.5, 300., .5), np.arange(0.5, 300., .5))
>>> exact = np.sin(np.sqrt (X ** 2 + Y ** 2) * np.pi / M)
>>> np.sum(np.abs(exact.flat - f.data))/(M * N * 4.) < 1e-5
True
"""

import numpy as np

from pymt.grids import UniformRectilinear, Rectilinear, Structured, Unstructured
from pymt.grids.igrid import (
    IGrid,
    IField,
    DimensionError,
    CenteringValueError,
    CENTERING_CHOICES,
)

try:
    import ESMF as esmf
except ImportError:
    esmf = None
    __doc__ = "This module is not available (no ESMF installation was found)"


class EsmpGrid(IGrid):
    def __init__(self):
        self._mesh = esmf.Mesh(parametric_dim=2, spatial_dim=2)

        self._mesh_add_nodes()
        self._mesh_add_elements()

        super(EsmpGrid, self).__init__()

    def get_point_count(self):
        raise NotImplementedError("get_point_count")

    def get_cell_count(self):
        raise NotImplementedError("get_cell_count")

    def as_mesh(self):
        return self._mesh

    def _mesh_add_nodes(self):
        node_ids = np.arange(1, self.get_point_count() + 1, dtype=int)
        (x, y) = (self.get_x(), self.get_y())

        node_coords = np.empty(x.size + y.size, dtype=np.float64)
        (node_coords[0::2], node_coords[1::2]) = (x, y)

        node_owner = np.zeros(self.get_point_count(), dtype=int)

        self._mesh.add_nodes(self.get_point_count(), node_ids, node_coords, node_owner)

    def _mesh_add_elements(self):
        cell_ids = np.arange(1, self.get_cell_count() + 1, dtype=int)
        cell_types = np.empty(self.get_cell_count(), dtype=int)
        cell_types.fill(esmf.MeshElemType.QUAD)

        cell_conn = np.array(self.get_connectivity(), dtype=int)  # + 1

        self._mesh.add_elements(self.get_cell_count(), cell_ids, cell_types, cell_conn)


class EsmpUnstructured(Unstructured, EsmpGrid):
    name = "ESMPUnstructured"


class EsmpStructured(Structured, EsmpGrid):
    name = "ESMPStructured"


class EsmpRectilinear(Rectilinear, EsmpGrid):
    name = "ESMPRectilinear"


class EsmpUniformRectilinear(UniformRectilinear, EsmpStructured):
    name = "ESMPUniformRectilinear"


class EsmpField(IField):
    def __init__(self, *args, **kwargs):
        super(EsmpField, self).__init__(*args, **kwargs)
        self._fields = {}

    def get_point_count(self):
        raise NotImplementedError("get_point_count")

    def get_cell_count(self):
        raise NotImplementedError("get_cell_count")

    def add_field(self, field_name, val, centering="zonal"):
        if centering not in CENTERING_CHOICES:
            raise CenteringValueError(centering)

        if centering == "zonal" and val.size != self.get_cell_count():
            raise DimensionError(val.size, self.get_cell_count())
        elif centering != "zonal" and val.size != self.get_point_count():
            raise DimensionError(val.size, self.get_point_count())

        if centering == "zonal":
            meshloc = esmf.MeshLoc.ELEMENT
        else:
            meshloc = esmf.MeshLoc.NODE

        field = esmf.Field(self._mesh, field_name, meshloc=meshloc)
        np.copyto(field.data, val.view().reshape(field.data.shape))
        self._fields[field_name] = field

    def get_field(self, field_name):
        return self._fields[field_name]

    def as_esmp(self, field_name):
        return self._fields[field_name]


class EsmpStructuredField(EsmpStructured, EsmpField):
    def add_field(self, field_name, val, centering="zonal"):
        if centering == "zonal":
            if val.ndim > 1 and np.any(val.shape != self.get_shape() - 1):
                raise DimensionError(val.shape, self.get_shape() - 1)
        elif centering != "zonal":
            if val.ndim > 1 and np.any(val.shape != self.get_shape()):
                raise DimensionError(val.shape, self.get_shape())
        try:
            super(EsmpStructuredField, self).add_field(
                field_name, val, centering=centering
            )
        except (DimensionError, CenteringValueError):
            raise


class EsmpUnstructuredField(EsmpUnstructured, EsmpField):
    pass


class EsmpRectilinearField(EsmpRectilinear, EsmpStructuredField):
    pass


class EsmpRasterField(EsmpUniformRectilinear, EsmpRectilinearField):
    pass


def run_regridding(srcfield, dstfield, **kwds):
    """run_regridding(source_field, destination_field, method=ESMP_REGRIDMETHOD_CONSERVE, unmapped=ESMP_UNMAPPEDACTION_ERROR)

    **PRECONDITIONS:**
        Two ESMP_Fields have been created and a regridding operation is desired from 'srcfield' to 'dstfield'.

    **POSTCONDITIONS:**
        An ESMP regridding operation has set the data on 'dstfield'.
    """
    method = kwds.get("method", esmf.RegridMethod.CONSERVE)
    unmapped = kwds.get("unmapped", esmf.UnmappedAction.ERROR)

    # call the regridding functions
    regridder = esmf.Regrid(
        srcfield, dstfield, regrid_method=method, unmapped_action=unmapped
    )
    dstfield = regridder(srcfield, dstfield)

    return dstfield
