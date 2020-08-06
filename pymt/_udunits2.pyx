# cython: language_level=3
import os
import pathlib
import pkg_resources
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


UDUNITS_ENCODING = {
    "ascii": UnitEncoding.ASCII,
    "us-ascii": UnitEncoding.ASCII,
    "iso-8859-1": UnitEncoding.ISO_8859_1,
    "iso8859-1": UnitEncoding.ISO_8859_1,
    "latin-1": UnitEncoding.LATIN1,
    "latin1": UnitEncoding.LATIN1,
    "utf-8": UnitEncoding.UTF8,
    "utf8": UnitEncoding.UTF8,
}


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


class UnitSystem(_UnitSystem):

    """A system of units.

    A unit-system is a set of units that are all defined in terms of
    the same set of base units. In the SI system of units, for example,
    the base units are the meter, kilogram, second, ampere, kelvin,
    mole, and candela. (For definitions of these base units,
    see http://physics.nist.gov/cuu/Units/current.html)

    In the UDUNITS-2 package, every accessible unit belongs to one and
    only one unit-system. It is not possible to convert numeric values
    between units of different unit-systems. Similarly, units belonging
    to different unit-systems always compare unequal.

    Parameters
    ----------
    filepath : str, optional
        Path to a *udunits2* xml-formatted unit database. If not provided,
        a default system of units is used.
    """
    def __init__(self, filepath=None):
        self._registry = dict()

    def __getitem__(self, key):
        try:
            return self._registry[key]
        except KeyError:
            pass
        self._registry[key] = self.Unit(key)
        return self._registry[key]


cdef class _UnitSystem:
    cdef ut_system* _unit_system
    cdef ut_status _status
    cdef char* _filepath

    def __cinit__(self, filepath=None):
        cdef char* path

        filepath, self._status = _UnitSystem.get_xml_path(filepath)
        as_bytes = str(filepath).encode("utf-8")

        self._filepath = <char*>malloc((len(as_bytes) + 1) * sizeof(char))
        strcpy(self._filepath, as_bytes)

        with suppress_stdout():
            self._unit_system = ut_read_xml(self._filepath)

        if self._unit_system == NULL:
            status = ut_get_status()
            raise UnitError(status)

    @staticmethod
    def get_xml_path(filepath=None):
        """Get the path to a unit database.

        Parameters
        ----------
        filepath : str, optional
            The path to an xml-formatted unit database. If not provided, use
            the value of the *UDUNITS2_XML_PATH* environment variable,
            otherwise use a default unit database.

        Returns
        -------
        str
            The path to a units database.
        """
        if filepath is None:
            try:
                filepath = os.environ["UDUNITS2_XML_PATH"]
            except KeyError:
                filepath = pkg_resources.resource_filename(
                    "pymt", "data/udunits/udunits2.xml"
                )
                status = UnitStatus.OPEN_DEFAULT
            else:
                status = UnitStatus.OPEN_ENV
        else:
            status = UnitStatus.OPEN_ARG
        return pathlib.Path(filepath), status

    def dimensionless_unit(self):
        """The dimensionless unit used by the unit system.

        Returns
        -------
        Unit
            The dimensionless unit of the system.
        """
        cdef ut_unit* unit = ut_get_dimensionless_unit_one(self._unit_system)
        if unit == NULL:
            raise UnitError(ut_get_status())
        return Unit.from_ptr(unit)

    def unit_by_name(self, name):
        """Get a unit from the system by name.

        Parameters
        ----------
        name : str
            Name of a unit.

        Returns
        -------
        Unit or None
            The unit of the system that *name* maps to. If no mapping exists,
            return ``None``.
        """
        unit = ut_get_unit_by_name(self._unit_system, name.encode("utf-8"))
        if unit == NULL:
            status = ut_get_status()
            if status == UnitStatus.SUCCESS:
                return None
            else:
                raise RuntimeError("system and/or name is NULL")
        return Unit.from_ptr(unit, owner=True)

    def unit_by_symbol(self, symbol):
        """Get a unit from the system by symbol.

        Parameters
        ----------
        symbol : str
            Symbol of a unit.

        Returns
        -------
        Unit or None
            The unit of the system that *symbol* maps to. If no mapping exists,
            return ``None``.
        """
        unit = ut_get_unit_by_symbol(self._unit_system, symbol.encode("utf-8"))
        if unit == NULL:
            status = ut_get_status()
            if status == UnitStatus.SUCCESS:
                return None
            else:
                raise RuntimeError("system and/or symbol is NULL")
        return Unit.from_ptr(unit, owner=True)

    def Unit(self, name):
        """Construct a unit from a unit string.

        Parameters
        ----------
        name : str
            Unit string.

        Returns
        -------
        Unit
            A new unit corresponding the the provided string.
        """
        unit = ut_parse(self._unit_system, name.encode("utf-8"), UnitEncoding.UTF8)
        if unit == NULL:
            status = ut_get_status()
            raise UnitNameError(name, status)
        return Unit.from_ptr(unit, owner=True)

    @property
    def database(self):
        """Path to the unit-database being used."""
        return pathlib.Path(self._filepath.decode())

    @property
    def status(self):
        """Status that indicates how the database was found.

        Returns
        -------
        str
            *'user'* if a user-supplied path was used, *'env'* if the path
            was provided by the *UDUNITS2_XML_PATH* environment variable, or
            *'default'* if the default path was used.
        """
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
        free(self._filepath)
        self._unit_system = NULL
        self._filepath = NULL
        self._status = UnitStatus.SUCCESS

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

    def to(self, unit):
        """Construct a unit converter to convert another unit.

        Parameters
        ----------
        unit : Unit
            The unit to convert to.

        Returns
        -------
        UnitConverter
            A converter that converts values to the provided unit.
        """
        return self.UnitConverter(unit)

    cpdef UnitConverter(self, Unit unit):
        converter = ut_get_converter(self._unit, unit._unit)

        if converter == NULL:
            status = ut_get_status()
            raise IncompatibleUnitsError(str(self), str(unit))

        return UnitConverter.from_ptr(converter, owner=True)

    def __dealloc__(self):
        if self._unit is not NULL and self.ptr_owner is True:
            ut_free(self._unit)
            self._unit = NULL
            self.ptr_owner = False


    def __str__(self):
        return self.format(encoding="ascii")

    def __repr__(self):
        return "Unit({0!r})".format(self.format(encoding="ascii"))

    cpdef compare(self, Unit other):
        """Compare units.

        Parameters
        ----------
        other : Unit
            A unit to compare to.

        Returns
        -------
        int
            A negative integer if this unit is less than the provided
            unit, 0 if they are equal, and a positive integer if this
            unit is greater.
        """
        return ut_compare(self._unit, other._unit)

    def __lt__(self, other):
        return self.compare(other) < 0

    def __le__(self, other):
        return self.compare(other) <= 0

    def __eq__(self, other):
        return self.compare(other) == 0

    def __ge__(self, other):
        return self.compare(other) >= 0

    def __gt__(self, other):
        return self.compare(other) > 0

    def __ne__(self, other):
        return self.compare(other) != 0

    def format(self, encoding="ascii", formatting=UnitFormatting.NAMES):
        try:
            unit_encoding = UDUNITS_ENCODING[encoding]
        except KeyError:
            raise ValueError("unknown encoding ({encoding})")

        str_len = ut_format(
            self._unit, self._buffer, 2048, opts=unit_encoding | formatting
        )
        if str_len >= 2048:
            raise ValueError("unit string is too large")

        return self._buffer.decode(encoding=encoding)

    @property
    def name(self):
        """Name of the unit.

        Returns
        -------
        str or None
            Name of the unit as a string or, ``None`` if no mapping exists.
        """
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
        """Symbol of the unit.

        Returns
        -------
        str or None
            Symbol of the unit as a string or, ``None`` if no mapping exists.
        """
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
        """Check if the unit is dimensionless.

        Returns
        -------
        bool
            ``True`` if the unit is dimensionless, otherwise ``False``.
        """
        return ut_is_dimensionless(self._unit) != 0

    cpdef is_convertible_to(self, Unit unit):
        return bool(ut_are_convertible(self._unit, unit._unit))


cdef class UnitConverter:

    """Convert numeric values between compatible units."""

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
        """Convert a value from one unit to another.

        Parameters
        ----------
        value ; number, or array-like
            The value or values to convert.
        out : array-like, optional
            If converting values from an array, the converted values
            will be placed here. To convert in-place, this can be
            the input array of values. If ``None``, a new array
            will be created to hold the converted values.

        Returns
        -------
        value or array-like
            The converted values or values.
        """
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
            self.ptr_owner = False
