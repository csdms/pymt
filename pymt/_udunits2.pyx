# cython: language_level=3
import numpy as np
cimport numpy as np


cdef extern from "udunits2.h":
    ctypedef struct ut_system:
        pass
    ctypedef struct ut_unit:
        pass
    ctypedef struct cv_converter:
        pass

    ut_system* ut_read_xml(const char * path)
    ut_unit* ut_parse(const ut_system* system, const char* string, int encoding)
    int ut_are_convertible(const ut_unit* unit1, const ut_unit* unit2)
    int ut_format(const ut_unit* unit, char* buf, size_t size, unsigned opts)
    cv_converter* ut_get_converter(ut_unit* const src, ut_unit* const dst)
    double cv_convert_double(const cv_converter* converter, const double value)
    double* cv_convert_doubles (const cv_converter* converter, const double* src, size_t count, double* dst)
    void cv_free(cv_converter* conv)
    void ut_free(ut_unit* unit)


cdef ut_system* unit_system = ut_read_xml(NULL)


cdef class _UnitConverter:
    cdef cv_converter* _conv
    cdef cv_converter* _inv

    def __cinit__(self, src, dst):
        src_unit = ut_parse(unit_system, src.encode("utf-8"), 0)
        dst_unit = ut_parse(unit_system, dst.encode("utf-8"), 0)
        self._conv = ut_get_converter(src_unit, dst_unit)
        self._inv = ut_get_converter(dst_unit, src_unit)
        if self._conv == NULL:
            raise ValueError("units are not convertible")

    def __call__(self, value, out=None, inverse=False):
        try:
            n_items = len(value)
        except TypeError:
            return self._convert_scalar(value, inverse=inverse)
        else:
            values = np.array(value, dtype=float)
            if out is None:
                out = np.empty_like(values)
            return self._convert_array(values, out)

    cdef _convert_scalar(self, value, inverse=False):
        converter = self._conv if not inverse else self._inv
        return cv_convert_double(converter, value)

    cdef _convert_array(
        self,
        np.ndarray[double, ndim=1] values,
        np.ndarray[double, ndim=1] out,
        inverse=False,
    ):
        converter = self._conv if not inverse else self._inv
        cv_convert_doubles(converter, &values[0], len(values), &out[0])
        return out

    def __dealloc__(self):
        cv_free(self._inv)
        cv_free(self._conv)


cdef class _Unit:
    cdef ut_unit* _unit
    cdef char[2048] _name

    def __cinit__(self, name):
        self._unit = ut_parse(unit_system, name.encode("utf-8"), 0)
        if self._unit == NULL:
            raise ValueError(f"invalid units: {name}")
        str_len = ut_format(self._unit, self._name, 2048, 4 | 8)
        if str_len >= 2048:
            raise ValueError("unit string is too large")
    
    def is_time(self):
        dst_unit = ut_parse(unit_system, "s".encode("utf-8"), 0)
        return bool(ut_are_convertible(self._unit, dst_unit))

    def convert_to(self, value, dst, out=None):
        return _UnitConverter(self._name.decode(), dst)(value, out=out)

    def convert_from(self, value, src, out=None):
        return _UnitConverter(src, self._name.decode())(value, out=out)

    def __dealloc__(self):
        ut_free(self._unit)
