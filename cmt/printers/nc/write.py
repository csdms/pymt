#! /usr/bin/env python
from warnings import warn

from ...grids.assertions import (is_rectilinear, is_structured)
from .ugrid import (NetcdfRectilinearField, NetcdfStructuredField,
                    NetcdfUnstructuredField)


def field_tofile(field, path, append=False, attrs=None, time=None,
                 time_units=None, time_reference=None,
                 long_name=None, fmt='NETCDF4', keep_open=False):
    if time_units is not None:
        warn('ignoring keyword "time_units"', UserWarning)
    if time_reference is not None:
        warn('ignoring keyword "time_reference"', UserWarning)
    if not keep_open:
        warn('resetting "keep_open" to True', UserWarning)

    attrs = attrs or {}
    long_name = long_name or {}
    args = (path, field)
    kwds = dict(append=append, fmt=fmt, time=time, keep_open=True)

    if is_rectilinear(field, strict=False):
        NetcdfRectilinearField(*args, **kwds)
    elif is_structured(field, strict=False):
        NetcdfStructuredField(*args, **kwds)
    else:
        NetcdfUnstructuredField(*args, **kwds)
