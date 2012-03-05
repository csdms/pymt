#! /bin/env python

import numpy as np
from igrid import IField, DimensionError, CenteringValueError, centering_choices
from raster import UniformRectilinear
from rectilinear import Rectilinear
from structured import Structured
from unstructured import Unstructured

class GridField (Unstructured, IField):
    def __init__ (self, *args, **kwargs):
        super (GridField, self).__init__ (*args, **kwargs) 
        self._fields = {}

    def add_field (self, field_name, val, centering='zonal'):
        if centering not in centering_choices:
            raise CenteringValueError (centering)

        if centering=='zonal' and val.size != self.get_cell_count ():
            raise DimensionError (val.size, self.get_cell_count ())
        elif centering!='zonal' and val.size != self.get_point_count ():
            raise DimensionError (val.size, self.get_point_count ())

        self._fields[field_name] = val
        self._fields[field_name].shape = val.size

    def get_field (self, field_name):
        return self._fields[field_name]

class StructuredField (Structured, GridField):
    def add_field (self, field_name, val, centering='zonal'):
        if centering=='zonal':
            if val.ndim > 1 and np.any (val.shape != self.get_shape ()-1):
                raise DimensionError (val.shape, self.get_shape ()-1)
        elif centering!='zonal':
            if val.ndim > 1 and np.any (val.shape != self.get_shape ()):
                raise DimensionError (val.shape, self.get_shape ())
        try:
            super (StructuredField, self).add_field (field_name, val, centering=centering)
        except DimensionError, CenteringValueError:
            raise

class RectilinearField (Rectilinear, StructuredField):
    pass
class RasterField (UniformRectilinear, StructuredField):
    """
Create a field that looks like this,

::

    (0) --- (1) --- (2)
     |       |       |
     |   0   |   1   |
     |       |       |
    (3) --- (4) --- (5)

Create the field,

    >>> g = RasterField ((2,3), (1,2), (0, 0), indexing='ij')
    >>> g.get_cell_count ()
    2
    >>> g.get_point_count ()
    6

Add some data at the points of our grid.

    >>> data = np.arange (6)
    >>> g.add_field ('var0', data, centering='point')
    >>> g.get_field ('var0')
    array([0, 1, 2, 3, 4, 5])

The data can be given either as a 1D array or with the same shape
as the point grid. In either case, though, it will be flattened.

    >>> data = np.arange (6)
    >>> data.shape = (2, 3)
    >>> g.add_field ('var0', data, centering='point')
    >>> g.get_field ('var0')
    array([0, 1, 2, 3, 4, 5])

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

Add data to the cells of the grid. Again, the data can be given
as a 1D array or with the same shape as the cell grid and if the
size or shape doesn't match raise an exception.

    >>> data = np.arange (2)
    >>> g.add_field ('var1', data, centering='zonal')
    >>> g.get_field ('var1')
    array([0, 1])

    >>> data = np.ones ((2, 1))
    >>> g.add_field ('bad var', data, centering='zonal')
    Traceback (most recent call last):
        ...
    DimensionError: (2, 1) != (1, 2)

    >>> data = np.arange (3)
    >>> g.add_field ('bad var', data, centering='zonal')
    Traceback (most recent call last):
        ...
    DimensionError: 3 != 2

    >>> data = np.array (3)
    >>> g.add_field ('bad var', data, centering='zonal')
    Traceback (most recent call last):
        ...
    DimensionError: 1 != 2

    """
    pass

if __name__ == '__main__':
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)


