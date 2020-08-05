# cython: language_level=3
import pathlib
from enum import Enum, Flag

import numpy as np
cimport numpy as np
from libc.stdlib cimport free, malloc
from libc.string cimport strcpy

from .errors import BadUnitError, IncompatibleUnitsError
from .utils.utils import suppress_stdout


class UnitError(Exception):

    def __init__(self, code, msg=""):
        self._code = code
        self._msg = msg

    def __str__(self):
        msg = self._msg or STATUS_MESSAGE.get(self._code, "Unknown")
        return "{0} (status {1})".format(msg, self._code)


class UnitNameError(UnitError):

    def __init__(self, name, code):
        self._name = name
        self._code = code

    def __str__(self):
        return "{0!r}: {1} (status {2})".format(
            self._name, STATUS_MESSAGE.get(self._code, "Unknown"), self._code
        )


class UnitEncoding(int, Enum):
    ASCII = 0
    ISO_8859_1 = 1
    LATIN1 = 1
    UTF8 = 2


class UnitFormatting(int, Flag):
    NAMES = 4
    DEFINITIONS = 8


class UnitStatus(int, Enum):
    SUCCESS = 0
    BAD_ARG = 1
    EXISTS = 2
    NO_UNIT = 3
    OS = 4
    NOT_SAME_SYSTEM = 5
    MEANINGLESS = 6
    NO_SECOND = 7
    VISIT_ERROR = 8
    CANT_FORMAT = 9
    SYNTAX = 10
    UNKNOWN = 11
    OPEN_ARG = 12
    OPEN_ENV = 13
    OPEN_DEFAULT = 14
    PARSE = 15


STATUS_MESSAGE = {
    UnitStatus.SUCCESS: "Success",
    UnitStatus.BAD_ARG:	"An argument violates the function's contract",
    UnitStatus.EXISTS: "Unit, prefix, or identifier already exists",
    UnitStatus.NO_UNIT: "No such unit exists",
    UnitStatus.OS: "Operating-system error.  See 'errno'",
    UnitStatus.NOT_SAME_SYSTEM: "The units belong to different unit-systems",
    UnitStatus.MEANINGLESS: "The operation on the unit(s) is meaningless",
    UnitStatus.NO_SECOND: "The unit-system doesn't have a unit named 'second'",
    UnitStatus.VISIT_ERROR: "An error occurred while visiting a unit",
    UnitStatus.CANT_FORMAT: "A unit can't be formatted in the desired manner",
    UnitStatus.SYNTAX: "string unit representation contains syntax error",
    UnitStatus.UNKNOWN: "string unit representation contains unknown word",
    UnitStatus.OPEN_ARG: "Can't open argument-specified unit database",
    UnitStatus.OPEN_ENV: "Can't open environment-specified unit database",
    UnitStatus.OPEN_DEFAULT: "Can't open installed, default, unit database",
    UnitStatus.PARSE: "Error parsing unit specification",
}


cdef extern from "udunits2.h":
    ctypedef struct ut_system:
        pass
    ctypedef struct ut_unit:
        pass
    ctypedef struct cv_converter:
        pass
    ctypedef int ut_encoding;
    ctypedef int ut_status;

    const char* ut_get_path_xml(const char* path, ut_status* status)
    ut_unit* ut_get_unit_by_symbol(const ut_system* system, const char* symbol)
    ut_unit* ut_get_unit_by_name(const ut_system* system, const char* name)

    ut_system* ut_read_xml(const char * path)
    ut_unit* ut_parse(const ut_system* system, const char* string, int encoding)
    ut_unit* ut_get_dimensionless_unit_one(const ut_system* system)
    void ut_free_system(ut_system* system)

    int ut_are_convertible(const ut_unit* unit1, const ut_unit* unit2)
    int ut_format(const ut_unit* unit, char* buf, size_t size, unsigned opts)
    const char* ut_get_name (const ut_unit* unit, ut_encoding encoding)
    const char* ut_get_symbol (const ut_unit* unit, ut_encoding encoding)
    ut_system* ut_get_system(const ut_unit* unit)
    int ut_is_dimensionless(const ut_unit* unit)
    int ut_compare(const ut_unit* unit1, const ut_unit* unit2)
    void ut_free(ut_unit* unit)

    cv_converter* ut_get_converter(ut_unit* const src, ut_unit* const dst)
    double cv_convert_double(const cv_converter* converter, const double value)
    double* cv_convert_doubles(
        const cv_converter* converter, const double* src, size_t count, double* dst
    )
    void cv_free(cv_converter* conv)

    ut_status ut_get_status()


cdef class UnitSystem:
    cdef ut_system* _unit_system
    cdef ut_status _status
    cdef char* _filepath
    cdef bint _own_filepath

    def __cinit__(self, filepath=None):
        cdef char* path

        if filepath is None:
            path = NULL
        else:
            as_bytes = str(filepath).encode("utf-8")
            path = as_bytes

        _filepath = ut_get_path_xml(path, &self._status)
        self._status = UnitStatus(self._status)

        if self._status in (UnitStatus.OPEN_ARG, UnitStatus.OPEN_ENV):
            self._filepath = <char*>malloc((len(_filepath) + 1) * sizeof(char))
            strcpy(self._filepath, _filepath)
            self._own_filepath = True
        else:
            self._filepath = _filepath
            self._own_filepath = False

        with suppress_stdout():
            self._unit_system = ut_read_xml(self._filepath)

        if self._unit_system == NULL:
            status = ut_get_status()
            raise UnitError(status)

    def dimensionless_unit(self):
        cdef ut_unit* unit = ut_get_dimensionless_unit_one(self._unit_system)
        if unit == NULL:
            raise UnitError(ut_get_status())
        return Unit.from_ptr(unit)

    def unit_by_name(self, name):
        unit = ut_get_unit_by_name(self._unit_system, name.encode("utf-8"))
        if unit == NULL:
            status = ut_get_status()
            if status == UnitStatus.SUCCESS:
                return None
            else:
                raise RuntimeError("system and/or name is NULL")
        return Unit.from_ptr(unit, owner=True)

    def unit_by_symbol(self, symbol):
        unit = ut_get_unit_by_symbol(self._unit_system, symbol.encode("utf-8"))
        if unit == NULL:
            status = ut_get_status()
            if status == UnitStatus.SUCCESS:
                return None
            else:
                raise RuntimeError("system and/or symbol is NULL")
        return Unit.from_ptr(unit, owner=True)

    def Unit(self, name):
        unit = ut_parse(self._unit_system, name.encode("utf-8"), UnitEncoding.UTF8)
        if unit == NULL:
            status = ut_get_status()
            raise UnitNameError(name, status)
        return Unit.from_ptr(unit, owner=True)

    @property
    def database(self):
        return pathlib.Path(self._filepath.decode())

    @property
    def status(self):
        if self._status == UnitStatus.OPEN_ARG:
            return "user"
        elif self._status == UnitStatus.OPEN_ENV:
            return "env"
        elif self._status == UnitStatus.OPEN_DEFAULT:
            return "default"
        else:
            raise RuntimeError("unknown unit_system status")

    def __dealloc__(self):
        ut_free_system(self._unit_system)
        if self._own_filepath:
            free(self._filepath)

    def __str__(self):
        return str(self.database)

    def __repr__(self):
        return "UnitSystem({0!r})".format(str(self.database))

    def __eq__(self, other):
        return self.database.samefile(other.database)


cdef class Unit:
    cdef ut_unit* _unit
    cdef bint ptr_owner
    cdef char[2048] _buffer

    @staticmethod
    cdef Unit from_ptr(ut_unit* unit_ptr, bint owner=False):
        if unit_ptr == NULL:
            raise RuntimeError("unit pointer is NULL")

        cdef Unit unit = Unit.__new__(Unit)
        unit._unit = unit_ptr
        unit.ptr_owner = owner
        return unit

    def __cinit__(self):
        self.ptr_owner = False

    def to(self, name):
        return self.UnitConverter(name)

    def UnitConverter(self, name):
        unit_ptr = ut_parse(
            ut_get_system(self._unit), name.encode("utf-8"), UnitEncoding.UTF8
        )

        if unit_ptr == NULL:
            status = ut_get_status()
            raise UnitNameError(name, status)
        else:
            unit = Unit.from_ptr(unit_ptr, owner=True)

        src, dst = self, unit

        converter = ut_get_converter(src._unit, dst._unit)

        if converter == NULL:
            status = ut_get_status()
            raise IncompatibleUnitsError(str(src), str(dst))

        return UnitConverter.from_ptr(converter, owner=True)

    def __dealloc__(self):
        if self._unit is not NULL and self.ptr_owner is True:
            ut_free(self._unit)
            self._unit = NULL


    def __str__(self):
        return self.format()

    def __repr__(self):
        return "Unit({0!r})".format(self.format())

    def __lt__(self, other):
        if not isinstance(other, Unit):
            type_ = type(other).__name__
            raise TypeError(
                f"'<' not supported between instances of 'Unit' and {type_!r}"
            )
        return ut_compare(self._unit, (<Unit>other)._unit) < 0

    def __le__(self, other):
        if not isinstance(other, Unit):
            type_ = type(other).__name__
            raise TypeError(
                f"'<=' not supported between instances of 'Unit' and {type_!r}"
            )
        return ut_compare(self._unit, (<Unit>other)._unit) <= 0

    def __eq__(self, other):
        if not isinstance(other, Unit):
            type_ = type(other).__name__
            raise TypeError(
                f"'==' not supported between instances of 'Unit' and {type_!r}"
            )
        return ut_compare(self._unit, (<Unit>other)._unit) == 0

    def __ge__(self, other):
        if not isinstance(other, Unit):
            type_ = type(other).__name__
            raise TypeError(
                f"'>=' not supported between instances of 'Unit' and {type_!r}"
            )
        return ut_compare(self._unit, (<Unit>other)._unit) >= 0

    def __gt__(self, other):
        if not isinstance(other, Unit):
            type_ = type(other).__name__
            raise TypeError(
                f"'>' not supported between instances of 'Unit' and {type_!r}"
            )
        return ut_compare(self._unit, (<Unit>other)._unit) > 0

    def __ne__(self, other):
        if not isinstance(other, Unit):
            type_ = type(other).__name__
            raise TypeError(
                f"'!=' not supported between instances of 'Unit' and {type_!r}"
            )
        return ut_compare(self._unit, (<Unit>other)._unit) != 0

    def format(self, opts=UnitEncoding.UTF8 | UnitFormatting.NAMES):
        str_len = ut_format(self._unit, self._buffer, 2048, opts)
        if str_len >= 2048:
            raise ValueError("unit string is too large")
        return self._buffer.decode()

    @property
    def name(self):
        name = ut_get_name(self._unit, 0)
        if name == NULL:
             status = ut_get_status()
             if status == UnitStatus.SUCCESS:
                 return None
             else:
                 raise UnitError(status)
        else:
            return name.decode()

    @property
    def symbol(self):
        symbol = ut_get_symbol(self._unit, 0)
        if symbol == NULL:
             status = ut_get_status()
             if status == UnitStatus.SUCCESS:
                 return None
             else:
                 raise UnitError(status)
        else:
            return symbol.decode()

    @property
    def is_dimensionless(self):
        return ut_is_dimensionless(self._unit) != 0

    def is_convertible_to(self, dst):
        return bool(ut_are_convertible(self._unit, (<Unit>dst)._unit))


cdef class UnitConverter:
    cdef cv_converter* _conv
    cdef bint ptr_owner

    @staticmethod
    cdef UnitConverter from_ptr(cv_converter* converter_ptr, bint owner=False):
        cdef UnitConverter converter = UnitConverter.__new__(UnitConverter)
        converter._conv = converter_ptr
        converter.ptr_owner = owner
        return converter

    def __cinit__(self):
        self.ptr_owner = False

    def __call__(self, value, out=None):
        try:
            n_items = len(value)
        except TypeError:
            return self._convert_scalar(value)
        else:
            values = np.array(value, dtype=float)
            if out is None:
                out = np.empty_like(values)
            return self._convert_array(values, out)

    cdef _convert_scalar(self, value):
        return cv_convert_double(self._conv, value)

    cdef _convert_array(
        self,
        np.ndarray[double, ndim=1] values,
        np.ndarray[double, ndim=1] out,
    ):
        cv_convert_doubles(self._conv, &values[0], len(values), &out[0])
        return out

    def __dealloc__(self):
        if self._conv is not NULL and self.ptr_owner is True:
            cv_free(self._conv)
            self._conv = NULL
