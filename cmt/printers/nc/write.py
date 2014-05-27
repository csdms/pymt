#! /usr/bin/env python

from ...grids.assertions import (is_rectilinear, is_structured,
                                 is_unstructured)
from .ugrid import (NetcdfRectilinearField, NetcdfStructuredField,
                    NetcdfUnstructuredField)


def field_tofile(field, path, append=False, attrs={}, time=None,
                 time_units='days', time_reference='00:00:00 UTC',
                 long_name={}, format='NETCDF4', keep_open=False):

    args = (path, field)
    kwds = dict(append=append, format=format, time=time, keep_open=True)

    if is_rectilinear(field, strict=False):
        NetcdfRectilinearField(*args, **kwds)
    elif is_structured(field, strict=False):
        NetcdfStructuredField(*args, **kwds)
    else:
        NetcdfUnstructuredField(*args, **kwds)
