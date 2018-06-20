#! /bin/env python
import types

import numpy as np
import six

from .igrid import (IField, DimensionError, CenteringValueError,
                    CENTERING_CHOICES)
from .raster import UniformRectilinear
from .rectilinear import Rectilinear
from .structured import Structured
from .unstructured import Unstructured


def combine_args_to_list (*args, **kwds):
    if len (args) == 0:
        args = kwds.get ('default', [])
    args = list (args)
    combined_args = []
    for arg in args:
        if isinstance (arg, six.string_types):
            combined_args.append (arg)
        else:
            combined_args.extend (arg)
    return combined_args


class GridField (Unstructured, IField):
    def __init__ (self, *args, **kwargs):
        super (GridField, self).__init__ (*args, **kwargs) 
        self._fields = {}
        self._field_units = {}

    def add_field (self, field_name, val, centering='zonal', units='-',
                   exist_action='clobber', time=None):
        assert (exist_action in ['clobber', 'append'])

        try:
            val.shape = val.size
        except AttributeError:
            val = np.array (val)

        if centering not in CENTERING_CHOICES:
            raise CenteringValueError (centering)

        if centering=='zonal' and val.size != self.get_cell_count ():
            raise DimensionError (val.size, self.get_cell_count ())
        elif centering!='zonal' and val.size != self.get_point_count ():
            raise DimensionError (val.size, self.get_point_count ())

        self._field_times = {}
        if field_name not in self._fields or exist_action == 'clobber':
            self._fields[field_name] = [val]
            self._field_times[field_name] = [time]
        else:
            self._fields[field_name].append (val)
            self._field_times[field_name].append (time)
        self._field_units[field_name] = units

        #self._fields[field_name].shape = val.size

    def pop_field (self, field_name, *args, **kwds):
        return_with_time = kwds.get ('return_with_time', False)

        field = self._fields[field_name].pop (*args)
        if return_with_time:
            time =  self._field_times[field_name].pop (*args)
            return (time, field)
        else:
            return field

    def get_field (self, field_name):
        if len (self._fields[field_name]) == 1:
            return self._fields[field_name][0]
        else:
            return self._fields[field_name]

    def get_field_units (self, field_name):
        return self._field_units[field_name]
    def set_field_units (self, field_name, units):
        try:
            self._field_units[field_name] = units
        except KeyError:
            pass
    def get_point_fields (self, *args):
        names = combine_args_to_list (*args, default=self._fields.keys ())

        fields = {}
        for name in names:
            array = self.get_field (name)
            if array.size == self.get_point_count ():
                fields[name] = array
        return fields

        #fields = {}
        #for (field, array) in self._fields.items ():
        #    if array.size == self.get_point_count ():
        #        fields[field] = array
        #return fields
    def get_cell_fields (self, *args):
        names = combine_args_to_list (*args, default=self._fields.keys ())

        fields = {}
        for name in names:
            array = self.get_field (name)
            if array.size == self.get_cell_count ():
                fields[name] = array
        return fields

    def items (self):
        return self._fields.items ()
    def keys (self):
        return self._fields.keys ()
    def values (self):
        return self._fields.values ()
    def has_field (self, name):
        return name in self._fields


class UnstructuredField (GridField):
    pass


class StructuredField (Structured, GridField):
    def add_field (self, field_name, val, centering='zonal', units='-'):
        if not hasattr(val, 'ndim'):
            val = np.array(val)
        #try:
        #    ndim = val.ndim
        #except AttributeError:
        #    val = np.array (val)
        #    ndim = val.ndim

        if centering=='zonal':
            if val.ndim > 1 and np.any (val.shape != self.get_shape ()-1):
                raise DimensionError (val.shape, self.get_shape ()-1)
        elif centering!='zonal':
            if val.ndim > 1 and np.any (val.shape != self.get_shape ()):
                raise DimensionError (val.shape, self.get_shape ())
        try:
            super (StructuredField, self).add_field (field_name, val, centering=centering, units=units)
        except (DimensionError, CenteringValueError):
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


A 1D-Field,

    >>> g = RasterField ((6, ), (1.5, ), (0.5, ), indexing='ij')
    >>> g.get_point_count ()
    6
    >>> g.get_cell_count ()
    5

    >>> point_data = np.arange (6.)
    >>> g.add_field ('Point Data', point_data, centering='point')

    >>> cell_data = np.arange (5.)*10.
    >>> g.add_field ('Cell Data', cell_data, centering='zonal')

    >>> g.get_field ('Cell Data')
    array([  0.,  10.,  20.,  30.,  40.])

    >>> g.get_field ('Point Data')
    array([ 0.,  1.,  2.,  3.,  4.,  5.])


A 3D-Field,

    >>> g = RasterField ((4, 3, 2), (1.5, 1., 3), (0.5, 0, -.5 ), indexing='ij')
    >>> g.get_point_count ()
    24
    >>> g.get_cell_count ()
    6

    >>> g.add_field ('Point Data', g.get_x (), centering='point')

    >>> cell_data = np.arange (6.)*10.
    >>> g.add_field ('Cell Data', cell_data, centering='zonal')

    >>> g.get_field ('Cell Data')
    array([  0.,  10.,  20.,  30.,  40.,  50.])

    >>> g.get_field('Point Data')
    array([-0.5,  2.5, -0.5,  2.5, -0.5,  2.5, -0.5,  2.5, -0.5,  2.5, -0.5,
            2.5, -0.5,  2.5, -0.5,  2.5, -0.5,  2.5, -0.5,  2.5, -0.5,  2.5,
           -0.5,  2.5])

    >>> g.get_shape()
    array([4, 3, 2])

    >>> g.get_x().size == g.get_field('Point Data').size
    True
    >>> x = g.get_x()
    >>> x.shape
    (24,)
    >>> x.shape = g.get_shape()
    >>> x.shape
    (4, 3, 2)

    """
    pass

if __name__ == '__main__':
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)


