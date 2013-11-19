#! /usr/bin/env python

from cmt.grids.assertions import (is_rectilinear, is_structured,
                                  is_unstructured)
from cmt.nc.ugrid import (NetcdfRectilinearField, NetcdfStructuredField,
                          NetcdfUnstructuredField)

def field_tofile(field, path, append=False, attrs={}, time=None,
                 time_units='days', time_reference='00:00:00 UTC',
                 long_name={}, format='NETCDF4'):

    if is_rectilinear(field, strict=False):
        NetcdfRectilinearField(path, field, append=append, format=format)
    elif is_structured(field, strict=False):
        NetcdfStructuredField(path, field, append=append, format=format)
    else:
        NetcdfUnstructuredField(path, field, append=append, format=format)
