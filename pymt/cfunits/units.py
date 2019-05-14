from __future__ import print_function

import ctypes
import netCDF4
import operator
import os
import sys

from numpy import array     as numpy_array
from numpy import dtype     as numpy_dtype
from numpy import empty     as numpy_empty
from numpy import generic   as numpy_generic
from numpy import ndarray   as numpy_ndarray
from numpy import ones      as numpy_ones
from numpy import reshape   as numpy_reshape
from numpy import where     as numpy_where
from numpy import zeros     as numpy_zeros


def _bytes_to_str(byte_string):
    """Convert a byte string to a regular string."""
    try:
        as_string = byte_string.decode()
    except AttributeError:
        as_string = byte_string
    finally:
        return str(as_string)


# --------------------------------------------------------------------
# Aliases for ctypes
# --------------------------------------------------------------------
_sizeof_buffer = 257
_string_buffer = ctypes.create_string_buffer(_sizeof_buffer)
_c_char_p      = ctypes.c_char_p
_c_int         = ctypes.c_int
_c_uint        = ctypes.c_uint
_c_float       = ctypes.c_float
_c_double      = ctypes.c_double
_c_size_t      = ctypes.c_size_t
_c_void_p      = ctypes.c_void_p
_pointer       = ctypes.pointer
_POINTER       = ctypes.POINTER

_ctypes_POINTER = {4: _POINTER(_c_float),
                   8: _POINTER(_c_double)}

# --------------------------------------------------------------------
# Load the Udunits-2 library and read the database
# --------------------------------------------------------------------
if sys.platform == 'darwin':
    # This has been tested on Mac OSX 10.5.8 and 10.6.8
    _udunits = ctypes.CDLL('libudunits2.0.dylib')
elif sys.platform.startswith("linux"):
    # Linux
    _udunits = ctypes.CDLL('libudunits2.so.0')
else:
    _udunits = ctypes.CDLL('udunits2.dll')
#--- End: if

# Suppress "overrides prefixed-unit" messages. This also suppresses
# all other error messages - so watch out!
#
# Messages may be turned back on by calling the module function
# udunits_error_messages.
# ut_error_message_handler ut_set_error_message_handler(
#                                   ut_error_message_handler handler);
_ut_set_error_message_handler = _udunits.ut_set_error_message_handler
_ut_set_error_message_handler.argtypes = (_c_void_p, )
_ut_set_error_message_handler.restype = _c_void_p

_ut_set_error_message_handler(_udunits.ut_ignore)

# Read the data base
# ut_system* ut_read_xml(const char* path);
_ut_read_xml = _udunits.ut_read_xml
_ut_read_xml.argtypes = (_c_char_p, )
_ut_read_xml.restype = _c_void_p

#print('units: before _udunits.ut_read_xml(',_unit_database,')')
if sys.platform == 'darwin' or sys.platform.startswith("linux"):
    path_to_xml = None  # Use the default path
else:
    path_to_xml = _c_char_p(
        os.path.join(
            sys.prefix,
            "lib/site-packages/cfunits/etc/udunits/udunits2.xml"
        ).encode("utf-8")
    )
_ut_system = _ut_read_xml(path_to_xml)
#print('units: after  _udunits.ut_read_xml(',_unit_database,')')

# Reinstate the reporting of error messages
#_ut_set_error_message_handler(_udunits.ut_write_to_stderr)

# --------------------------------------------------------------------
# Aliases for the UDUNITS-2 C API. See
# http://www.unidata.ucar.edu/software/udunits/udunits-2.0.4/udunits2lib.html
# for documentation.
# --------------------------------------------------------------------
# int ut_format(const ut_unit* const unit, char* buf, size_t size, unsigned opts);
_ut_format          = _udunits.ut_format
_ut_format.argtypes = (_c_void_p, _c_char_p, _c_size_t, _c_uint)
_ut_format.restype  = _c_int

# char* ut_trim(char* const string, const ut_encoding encoding);
_ut_trim            = _udunits.ut_trim
_ut_trim.argtypes   = (_c_char_p, _c_int) # ut_encoding assumed to be int!
_ut_trim.restype    = _c_char_p

# ut_unit* ut_parse(const ut_system* const system,
#                   const char* const string, const ut_encoding encoding);
_ut_parse           = _udunits.ut_parse
_ut_parse.argtypes = (_c_void_p, _c_char_p, _c_int) # ut_encoding assumed to be int!
_ut_parse.restype = _c_void_p

# int ut_compare(const ut_unit* const unit1, const ut_unit* const
#                unit2);
_ut_compare         = _udunits.ut_compare
_ut_compare.argtypes = (_c_void_p, _c_void_p)
_ut_compare.restype = _c_int

# int ut_are_convertible(const ut_unit* const unit1, const ut_unit*
#                        const unit2);
_ut_are_convertible = _udunits.ut_are_convertible
_ut_are_convertible.argtypes = (_c_void_p, _c_void_p)
_ut_are_convertible.restype = _c_int

# cv_converter* ut_get_converter(ut_unit* const from, ut_unit* const
#                                to);
_ut_get_converter   = _udunits.ut_get_converter
_ut_get_converter.argtypes = (_c_void_p, _c_void_p)
_ut_get_converter.restype = _c_void_p

# ut_unit* ut_divide(const ut_unit* const numer, const ut_unit* const
#                    denom);
_ut_divide          = _udunits.ut_divide
_ut_divide.argtypes = (_c_void_p, _c_void_p)
_ut_divide.restype  = _c_void_p

# ut_unit* ut_offset(const ut_unit* const unit, const double offset);
_ut_offset          = _udunits.ut_offset
_ut_offset.argtypes = (_c_void_p, _c_double)
_ut_offset.restype  = _c_void_p

# ut_unit* ut_raise(const ut_unit* const unit, const int power);
_ut_raise           = _udunits.ut_raise
_ut_raise.argtypes  = (_c_void_p, _c_int)
_ut_raise.restype   = _c_void_p

# ut_unit* ut_scale(const double factor, const ut_unit* const unit);
_ut_scale           = _udunits.ut_scale
_ut_scale.argtypes  = (_c_double, _c_void_p)
_ut_scale.restype   = _c_void_p

# ut_unit* ut_multiply(const ut_unit* const unit1, const ut_unit*
#                      const unit2);
_ut_multiply        = _udunits.ut_multiply
_ut_multiply.argtypes = (_c_void_p, _c_void_p)
_ut_multiply.restype = _c_void_p

# ut_unit* ut_log(const double base, const ut_unit* const reference);
_ut_log             = _udunits.ut_log
_ut_log.argtypes    = (_c_double, _c_void_p)
_ut_log.restype     = _c_void_p

# ut_unit* ut_root(const ut_unit* const unit, const int root);
_ut_root            = _udunits.ut_root
_ut_root.argtypes   = (_c_void_p, _c_int)
_ut_root.restype    = _c_void_p

# void ut_free_system(ut_system*  system);
_ut_free            = _udunits.ut_free
_ut_free.argypes    = (_c_void_p, )
_ut_free.restype    = None

# float* cv_convert_floats(const cv_converter* converter, const float*
#                          const in, const size_t count, float* out);
_cv_convert_floats  = _udunits.cv_convert_floats
_cv_convert_floats.argtypes = (_c_void_p, _c_void_p, _c_size_t, _c_void_p)
_cv_convert_floats.restype = _c_void_p

# double* cv_convert_doubles(const cv_converter* converter, const
#                            double* const in, const size_t count,
#                            double* out);
_cv_convert_doubles = _udunits.cv_convert_doubles
_cv_convert_doubles.argtypes = (_c_void_p, _c_void_p, _c_size_t, _c_void_p)
_cv_convert_doubles.restype = _c_void_p

# double cv_convert_double(const cv_converter* converter, const double
#                          value);
_cv_convert_double  = _udunits.cv_convert_double
_cv_convert_double.argtypes = (_c_void_p, _c_double)
_cv_convert_double.restype = _c_double

# void cv_free(cv_converter* const conv);
_cv_free            = _udunits.cv_free
_cv_free.argtypes   = (_c_void_p, )
_cv_free.restype    = None

_UT_ASCII      = 0
_UT_NAMES      = 4
_UT_DEFINITION = 8

_cv_convert_array = {4: _cv_convert_floats,
                     8: _cv_convert_doubles}

# Some function definitions necessary for the following
# changes to the unit system.
_ut_get_unit_by_name = _udunits.ut_get_unit_by_name
_ut_get_unit_by_name.argtypes = (_c_void_p, _c_char_p)
_ut_get_unit_by_name.restype = _c_void_p
_ut_get_status = _udunits.ut_get_status
_ut_get_status.restype = _c_int
_ut_unmap_symbol_to_unit = _udunits.ut_unmap_symbol_to_unit
_ut_unmap_symbol_to_unit.argtypes = (_c_void_p, _c_char_p, _c_int)
_ut_unmap_symbol_to_unit.restype = _c_int
_ut_map_symbol_to_unit = _udunits.ut_map_symbol_to_unit
_ut_map_symbol_to_unit.argtypes = (_c_char_p, _c_int, _c_void_p)
_ut_map_symbol_to_unit.restype = _c_int
_ut_map_unit_to_symbol = _udunits.ut_map_unit_to_symbol
_ut_map_unit_to_symbol.argtypes = (_c_void_p, _c_char_p, _c_int)
_ut_map_unit_to_symbol.restype = _c_int
_ut_map_name_to_unit = _udunits.ut_map_name_to_unit
_ut_map_name_to_unit.argtypes = (_c_char_p, _c_int, _c_void_p)
_ut_map_name_to_unit.restype = _c_int
_ut_map_unit_to_name = _udunits.ut_map_unit_to_name
_ut_map_unit_to_name.argtypes = (_c_void_p, _c_char_p, _c_int)
_ut_map_unit_to_name.restype = _c_int
_ut_new_base_unit = _udunits.ut_new_base_unit
_ut_new_base_unit.argtypes = (_c_void_p, )
_ut_new_base_unit.restype = _c_void_p

# Change Sv mapping. Both sievert and sverdrup are just aliases,
# so no unit to symbol mapping needs to be changed.
# We don't need to remove rem, since it was constructed with
# the correct sievert mapping in place; because that mapping
# was only an alias, the unit now doesn't depend on the mapping
# persisting.
assert(0 == _ut_unmap_symbol_to_unit(_ut_system, _c_char_p(b'Sv'), _UT_ASCII))
assert(0 == _ut_map_symbol_to_unit(_c_char_p(b'Sv'), _UT_ASCII,
                                   _ut_get_unit_by_name(_ut_system, _c_char_p(b'sverdrup'))))

if sys.platform == 'darwin' or sys.platform.startswith("linux"):
    # Add new base unit calendar_year
    calendar_year_unit = _ut_new_base_unit(_ut_system)
    assert(0 == _ut_map_symbol_to_unit(_c_char_p(b'cY'), _UT_ASCII, calendar_year_unit))
    assert(0 == _ut_map_unit_to_symbol(calendar_year_unit, _c_char_p(b'cY'), _UT_ASCII))
    assert(0 == _ut_map_name_to_unit(_c_char_p(b'calendar_year'), _UT_ASCII, calendar_year_unit))
    assert(0 == _ut_map_unit_to_name(calendar_year_unit, _c_char_p(b'calendar_year'), _UT_ASCII))
    assert(0 == _ut_map_name_to_unit(_c_char_p(b'calendar_years'), _UT_ASCII, calendar_year_unit))

# Add various aliases useful for CF.
def add_unit_alias(definition, symbol, singular, plural):
    unit = _ut_parse(_ut_system, _c_char_p(definition.encode('utf-8')), _UT_ASCII)
    if symbol is not None:
        assert(0 == _ut_map_symbol_to_unit(_c_char_p(symbol.encode('utf-8')), _UT_ASCII, unit))
    if singular is not None:
        assert(0 == _ut_map_name_to_unit(_c_char_p(singular.encode('utf-8')), _UT_ASCII, unit))
    if plural is not None:
        assert(0 == _ut_map_name_to_unit(_c_char_p(plural.encode('utf-8')), _UT_ASCII, unit))

add_unit_alias("1.e-3", "psu", "practical_salinity_unit", "practical_salinity_units")
add_unit_alias("calendar_year/12", "cM", "calendar_month", "calendar_months")
add_unit_alias("1", None, "level", "levels")
add_unit_alias("1", None, "layer", "layers")
add_unit_alias("1", None, "sigma_level", "sigma_levels")
add_unit_alias("1", "dB", "decibel", "debicels")
add_unit_alias("10 dB", None, "bel", "bels")

#_udunits.ut_get_unit_by_name(_udunits.ut_new_base_unit(_ut_system),
#                             _ut_system, 'calendar_year')

# --------------------------------------------------------------------
# Create a calendar year unit
# --------------------------------------------------------------------
#_udunits.ut_map_name_to_unit('calendar_year', _UT_ASCII,
#                             _udunits.ut_new_base_unit(_ut_system))

# --------------------------------------------------------------------
# Aliases for netCDF4.netcdftime classes
# --------------------------------------------------------------------
if netCDF4.__version__ < '1.4':
    _netCDF4_netcdftime_utime = netCDF4.netcdftime.utime
    _datetime                 = netCDF4.netcdftime.datetime
else:
    import cftime    
    _netCDF4_netcdftime_utime = cftime.utime
    _datetime                 = cftime.datetime
    
# --------------------------------------------------------------------
# Aliases for netCDF4.netcdftime functions
# --------------------------------------------------------------------
if netCDF4.__version__ < '1.4':
    try:
        _num2date = netCDF4.num2date
        _date2num = netCDF4.date2num
    except:
        _num2date = netCDF4.netcdftime.num2date
        _date2num = netCDF4.netcdftime.date2num
else:
    _num2date = cftime.num2date
    _date2num = cftime.date2num
    
_cached_ut_unit = {}
_cached_utime   = {}

# --------------------------------------------------------------------
# Save some useful units
# --------------------------------------------------------------------
# A time ut_unit (equivalent to 'day', 'second', etc.)
_day_ut_unit  = _ut_parse(_ut_system, _c_char_p(b'day'), _UT_ASCII)
_cached_ut_unit['days'] = _day_ut_unit
# A pressure ut_unit (equivalent to 'Pa', 'hPa', etc.)
_pressure_ut_unit = _ut_parse(_ut_system, _c_char_p(b'pascal'), _UT_ASCII)
_cached_ut_unit['pascal'] = _pressure_ut_unit
# A calendar time ut_unit (equivalent to 'cY', 'cM')
_calendartime_ut_unit = _ut_parse(_ut_system, _c_char_p(b'calendar_year'), _UT_ASCII)
_cached_ut_unit['calendar_year'] = _calendartime_ut_unit
# A dimensionless unit one (equivalent to '', '1', '2', etc.)
#_dimensionless_unit_one = _udunits.ut_get_dimensionless_unit_one(_ut_system)
#_cached_ut_unit['']  = _dimensionless_unit_one
#_cached_ut_unit['1'] = _dimensionless_unit_one

_dimensionless_unit_one = _ut_parse(_ut_system, _c_char_p(b'1'), _UT_ASCII)
_cached_ut_unit['']  = _dimensionless_unit_one
_cached_ut_unit['1'] = _dimensionless_unit_one

# --------------------------------------------------------------------
# Set the default calendar type according to the CF conventions
# --------------------------------------------------------------------
_default_calendar = 'gregorian'
_canonical_calendar = {'gregorian'          : 'gregorian'          ,
                       'standard'           : 'gregorian'          ,
                       'none'               : 'gregorian'          ,
                       'proleptic_gregorian': 'proleptic_gregorian',
                       '360_day'            : '360_day'            ,
                       'noleap'             : '365_day'            ,
                       '365_day'            : '365_day'            ,
                       'all_leap'           : '366_day'            ,
                       '366_day'            : '366_day'            ,
                       'julian'             : 'julian'             ,
                       }

## --------------------------------------------------------------------
## Set month lengths in days for non-leap years (_days_in_month[0,1:])
## and leap years (_days_in_month[1,1:])
## --------------------------------------------------------------------
#_days_in_month = numpy_array(
#    [[-99, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
#     [-99, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]])

# --------------------------------------------------------------------
# Function to control Udunits error messages
# --------------------------------------------------------------------
def udunits_error_messages(flag):
    '''

Control the printing of error messages from Udunits, which are turned
off by default.

:Parameters:

    flag : bool
        Set to True to print Udunits error messages and False to not
        print Udunits error messages.

:Returns:

    None

:Examples:

>>> udunits_error_messages(True)
>>> udunits_error_messages(False)

'''
    if flag:
        _ut_set_error_message_handler(_udunits.ut_write_to_stderr)
    else:
        _ut_set_error_message_handler(_udunits.ut_ignore)
#--- End: def

#def _month_length(year, month, calendar, _days_in_month=_days_in_month):
#    '''
#
#Find month lengths in days for each year/month pairing in the input
#numpy arrays 'year' and 'month', both of which must have the same
#shape. 'calendar' must be one of the standard CF calendar types.
#
#:Parameters:
#
#
#'''
#    shape = month.shape
#    if calendar in ('standard', 'gregorian'):
#        leap = numpy_where(year % 4 == 0, 1, 0)
#        leap = numpy_where((year > 1582) &
#                           (year % 100 == 0) & (year % 400 != 0),
#                           0, leap)
#    elif calendar == '360_day':
#        days_in_month = numpy_empty(shape)
#        days_in_month.fill(30)
#        return days_in_month
#
#    elif calendar in ('all_leap', '366_day'):
#        leap = numpy_zeros(shape)
#
#    elif calendar in ('no_leap', '365_day'):
#        leap = numpy_ones(shape)
#
#    elif calendar == 'proleptic_gregorian':
#        leap = numpy_where(year % 4 == 0, 1, 0)
#        leap = numpy_where((year % 100 == 0) & (year % 400 != 0),
#                           0, leap)
#
#    days_in_month = numpy_array([_days_in_month[l, m]
#                                 for l, m in zip(leap.flat, month.flat)])
#    days_in_month.resize(shape)
#
#    return days_in_month
##--- End: def
#
#def _proper_date(year, month, day, calendar, fix=False,
#                 _days_in_month=_days_in_month):
#    '''
#
#Given equally shaped numpy arrays of 'year', 'month', 'day' adjust
#them *in place* to be proper dates. 'calendar' must be one of the
#standard CF calendar types.
#
#Excessive number of months are converted to years but excessive days
#are not converted to months nor years. If a day is illegal in the
#proper date then a ValueError is raised, unless 'fix' is True, in
#which case the day is lowered to the nearest legal date:
#
#    2000/26/1 -> 2002/3/1
#
#    2001/2/31 -> ValueError if 'fix' is False
#    2001/2/31 -> 2001/2/28  if 'fix' is True
#    2001/2/99 -> 2001/2/28  if 'fix' is True
#
#:Parameters:
#
#'''
##    y, month = divmod(month, 12)
##    year += y
#
#    year      += month // 12
#    month[...] = month % 12
#
#    mask       = (month == 0)
#    year[...]  = numpy_where(mask, year-1, year)
#    month[...] = numpy_where(mask, 12, month)
#    del mask
#
#    days_in_month = _month_length(year, month, calendar,
#                                  _days_in_month=_days_in_month)
#
#    if fix:
#        day[...] = numpy_where(day > days_in_month, days_in_month, day)
#    elif (day > days_in_month).any():
#        raise ValueError("Illegal date(s) in %s calendar" % calendar)
#
#    return year, month, day
##--- End: def


# ====================================================================
#
# Units object
#
# ====================================================================

class Units(object):
    '''Store, combine and compare physical units and convert numeric values
to different units.

Units are as defined in UNIDATA's Udunits-2 package, with a few
exceptions for greater consistency with the CF conventions namely
support for CF calendars and new units definitions.


**Modifications to the standard Udunits database**

Whilst a standard Udunits-2 database may be used, greater consistency
with CF is achieved by using a modified database. The following units
are either new to, modified from, or removed from the standard
Udunits-2 database (version 2.1.24):

=======================  ======  ============  ==============
Unit name                Symbol  Definition    Status
=======================  ======  ============  ==============
practical_salinity_unit  psu     1e-3          New unit
level                            1             New unit
sigma_level                      1             New unit
layer                            1             New unit
decibel                  dB      1             New unit
bel                              10 dB         New unit
sverdrup                 Sv      1e6 m3 s-1    Added symbol
sievert                          J kg-1        Removed symbol
=======================  ======  ============  ==============

Plural forms of the new units' names are allowed, such as
``practical_salinity_units``.

The modified database is in the *udunits* subdirectory of the *etc*
directory found in the same location as this module.


**Accessing units**

Units may be set, retrieved and deleted via the `units` attribute. Its
value is a string that can be recognized by UNIDATA's Udunits-2
package, with the few exceptions given in the CF conventions.

>>> u = Units('m s-1')
>>> u
<Cf Units: 'm s-1'>
>>> u.units = 'days since 2004-3-1'
>>> u
<CF Units: days since 2004-3-1>


**Equality and equivalence of units**

There are methods for assessing whether two units are equivalent or
equal. Two units are equivalent if numeric values in one unit are
convertible to numeric values in the other unit (such as
``kilometres`` and ``metres``). Two units are equal if they are
equivalent and their conversion is a scale factor of 1 and an offset
of 0 (such as ``kilometres`` and ``1000 metres``). Note that
equivalence and equality are based on internally stored binary
representations of the units, rather than their string
representations.

>>> u = Units('m/s')
>>> v = Units('m s-1')
>>> w = Units('km.s-1')
>>> x = Units('0.001 kilometer.second-1')
>>> y = Units('gram')

>>> u.equivalent(v), u.equals(v),  u == v
(True, True, True)
>>> u.equivalent(w), u.equals(w)
(True, False)
>>> u.equivalent(x), u.equals(x)
(True, True)
>>> u.equivalent(y), u.equals(y)
(False, False)


**Time and reference time units**

Time units may be given as durations of time (*time units*) or as an
amount of time since a reference time (*reference time units*):

>>> v = Units()
>>> v.units = 's'
>>> v.units = 'day'
>>> v.units = 'days since 1970-01-01'
>>> v.units = 'seconds since 1992-10-8 15:15:42.5 -6:00'

.. note::

   It is recommended that the units ``year`` and ``month`` be used
   with caution, as explained in the following excerpt from the CF
   conventions: "The Udunits package defines a year to be exactly
   365.242198781 days (the interval between 2 successive passages of
   the sun through vernal equinox). It is not a calendar year. Udunits
   includes the following definitions for years: a common_year is 365
   days, a leap_year is 366 days, a Julian_year is 365.25 days, and a
   Gregorian_year is 365.2425 days. For similar reasons the unit
   ``month``, which is defined to be exactly year/12, should also be
   used with caution."

**Calendar**

The date given in reference time units is associated with one of the
calendars recognized by the CF conventions and may be set with the
`calendar` attribute. However, as in the CF conventions, if the
calendar is not set then, for the purposes of calculation and
comparison, it defaults to the mixed Gregorian/Julian calendar as
defined by Udunits:

>>> u = Units('days since 2000-1-1')
>>> u.calendar
AttributeError: Can't get 'Units' attribute 'calendar'
>>> v = Units('days since 2000-1-1')
>>> v.calendar = 'gregorian'
>>> v.equals(u)
True


**Invalid units**

If the string defining the units is not a valid UDUNITS2 string (or
one of the CF exceptions, see above) then no exception is raised, but
the `isvalid` attribute returns `False` instead of `True`:

>>> u = Units('M/S')
>>> u
<CF Units: M/S (not valid)>
>>> u.isvalid
False
>>> print(u)
'M/S'
>>> v = Units('m/s')
>>> v
<CF Units: m/s>
>>> v.isvalid
True
>>> print(v)
'm/s'


**Arithmetic with units**

The following operators, operations and assignments are overloaded:

Comparison operators:

    ``==, !=``

Binary arithmetic operations:

    ``+, -, *, /, pow(), **``

Unary arithmetic operations:

    ``-, +``

Augmented arithmetic assignments:

    ``+=, -=, *=, /=, **=``

The comparison operations return a boolean and all other operations
return a new units object or modify the units object in place.

>>> u = Units('m')
<CF Units: m>

>>> v = u * 1000
>>> v
<CF Units: 1000 m>

>>> u == v
False
>>> u != v
True

>>> u **= 2
>>> u
<CF Units: m2>

It is also possible to create the logarithm of a unit corresponding to
the given logarithmic base:

>>> u = Units('seconds')
>>> u.log(10)
<CF Units: lg(re 1 s)>


**Modifying data for equivalent units**

Any numpy array or python numeric type may be modified for equivalent
units using the `conform` static method.

>>> Units.conform(2, Units('km'), Units('m'))
2000.0

>>> import numpy
>>> a = numpy.arange(5.0)
>>> Units.conform(a, Units('minute'), Units('second'))
array([   0.,   60.,  120.,  180.,  240.])
>>> a
array([ 0.,  1.,  2.,  3.,  4.])

If the *inplace* keyword is True, then a numpy array is modified in
place, without any copying overheads:

>>> Units.conform(a,
                  Units('days since 2000-12-1'),
                  Units('days since 2001-1-1'), inplace=True)
array([-31., -30., -29., -28., -27.])
>>> a
array([-31., -30., -29., -28., -27.])

    '''
    def __init__(self, units=None, calendar=None, formatted=False,
                 names=False, definition=False, _ut_unit=None):
        '''

**Initialization**

:Parameters:

    units: `str` or `cf.Units`, optional
        Set the new units from this string.

    calendar: `str`, optional
        Set the calendar for reference time units.

    formatted: `bool`, optional
        Format the string representation of the units in a
        standardized manner. See the `formatted` method.

    names: `bool`, optional
        Format the string representation of the units using names
        instead of symbols. See the `format` method.

    definition: `bool`, optional
        Format the string representation of the units using basic
        units. See the `format` method.

    _ut_unit: `int`, optional
        Set the new units from this Udunits binary unit
        representation. This should be an integer returned by a call
        to `ut_parse` function of Udunits. Ignored if `units` is set.

'''
        self._isvalid = True
        self._message = None

        if isinstance(units, self.__class__):
            self.__dict__ = units.__dict__
            return

        # Set the calendar
        _calendar = None
        if calendar is not None:
            _calendar = _canonical_calendar.get(calendar.lower())
            if _calendar is None:
                self._isvalid = False
                self._message = 'unknown calendar: {!r}'.format(calendar)
                _calendar = calendar
        #--- End: if
        
        if units is not None:
            units = _bytes_to_str(units)
            try:
                units = units.strip()
            except AttributeError:
                raise ValueError("Can't set unsupported unit: {!r}".format(units))

            if ' since ' in units:
                # --------------------------------------------------------
                # Set a reference time unit
                # --------------------------------------------------------
                # Set the calendar
                if calendar is None:
                    _calendar = _default_calendar
#                else:
#                    _calendar = _canonical_calendar[calendar.lower()]

                units_split = units.split(' since ')
                unit        = units_split[0].strip()
                
                ut_unit = _cached_ut_unit.get(unit, None)
                if ut_unit is None:                    
                    ut_unit = _ut_parse(_ut_system, _c_char_p(unit.encode('utf-8')), _UT_ASCII)
                    if not ut_unit or not _ut_are_convertible(ut_unit, _day_ut_unit):
                        ut_unit = None
                        self._isvalid = False
                    else:
                        _cached_ut_unit[unit] = ut_unit
                #--- End: if
                
#                ut_unit = _cached_ut_unit.get(unit, None)
#                if ut_unit is None:                    
#                    ut_unit = _ut_parse(_ut_system, _c_char_p(unit), _UT_ASCII)
#                    if not ut_unit or not _ut_are_convertible(ut_unit, _day_ut_unit):
#                        raise ValueError(
#                            "Can't set unsupported unit in reference time: '%s'" % 
#                            value)
#                    _cached_ut_unit[unit] = ut_unit
#                #--- End: if

                utime = _cached_utime.get((_calendar, units), None)

                if not utime:                       
                    # Create a new Utime object
                    unit_string = '%s since %s' % (unit, units_split[1].strip())
                    utime = _cached_utime.get((_calendar, unit_string), None)

                    if utime is None:
                        try:
                            utime = Utime(_calendar, unit_string)
                        except ValueError as error:
                            # Assume that the value error came from
                            # Utime complaining about the units. In
                            # this case, change the units to something
                            # acceptable to Utime and afterwards
                            # overwrite the Utime.units and
                            # Utime.unit_string attributes with the
                            # correct values. If this assumption was
                            # incorrect, then we'll just end up with
                            # another error, this time untrapped
                            # (possibly due to a wrong calendar).
                            self._isvalid = False
                            self._message = str(error)
                            utime = Utime(_calendar,)
#                                         'days since %s' % units_split[1].strip())
                            utime.unit_string = unit_string
                            utime.units       = unit
                        #--- End: try
                        _cached_utime[(_calendar, unit_string)] = utime
                    #--- End: if
                    _cached_utime[(calendar, units)] = utime
                #--- End: if

                self._isreftime = True
                self._calendar  = calendar
                self._utime     = utime
            
            else:
                # ----------------------------------------------------
                # Set a unit other than a reference time unit
                # ----------------------------------------------------
                ut_unit = _cached_ut_unit.get(units, None)
                if ut_unit is None:
                    ut_unit = _ut_parse(_ut_system, _c_char_p(units.encode('utf-8')), _UT_ASCII)
                    if not ut_unit:
                        ut_unit = None
                        self._isvalid = False
                    else:
                        _cached_ut_unit[units] = ut_unit
                #--- End: if
 
#                if ut_unit is None:
#                    ut_unit = _ut_parse(_ut_system, _c_char_p(units), _UT_ASCII)
#                    if not ut_unit:
#                        raise ValueError(
#                            "Can't set unsupported unit: %r" % units)
#                    _cached_ut_unit[units] = ut_unit
#                #--- End: if

                self._isreftime = False
                self._calendar  = None
                self._utime     = None
            #--- End: if

            self._ut_unit = ut_unit
            self._units   = units

            if formatted or names or definition:
                self._units = self.formatted(names, definition)

            return

        elif calendar:
            #---------------------------------------------------------
            # Calendar is set, but units are not.
            #---------------------------------------------------------
            self._units     = None
            self._ut_unit   = None
            self._isreftime = True
            self._calendar  = calendar
            self._utime     = Utime(_canonical_calendar[calendar.lower()])

            return
        #--- End: if

        if _ut_unit is not None:
            #---------------------------------------------------------
            # _ut_unit is set
            #---------------------------------------------------------
            self._ut_unit = _ut_unit
            self._isreftime = False

            units = _bytes_to_str(self.formatted(names, definition))
            _cached_ut_unit[units] = _ut_unit
            self._units = units

            self._calendar  = None
            self._utime     = None
            return
        #--- End: if

        #-------------------------------------------------------------
        # Nothing has been set
        #-------------------------------------------------------------
        self._units     = None
        self._ut_unit   = None 
        self._isreftime = False
        self._calendar  = None        
        self._utime     = None
    #--- End: def

#    def __getstate__(self):
#        '''
#
#Called when pickling.
#
#:Parameters:
#
#    None
#
#:Returns:
#
#    out : dict
#        A dictionary of the instance's attributes
#
#:Examples:
#
#>>> u = cf.Units('days since 3-4-5', calendar='gregorian')
#>>> u.__getstate__()
#{'calendar': 'gregorian',
# 'units': 'days since 3-4-5'}
#
#'''
#        return dict([(attr, getattr(self, attr))
#                     for attr in ('calendar', 'units') if hasattr(self, attr)])
#    #--- End: def        
#
#    def __setstate__(self, odict):
#        '''
#
#Called when unpickling.
#
#:Parameters:
#
#    odict : dict
#        The output from the instance's `__getstate__` method.
#
#:Returns:
#
#    None
#
#'''
#        for attr, value in odict.iteritems():
#            setattr(self, attr, value)
#     #--- End: def

#    def __hash__(self):
#        '''
#x.__hash__() <==> hash(x)
#
#'''
##        if not self:
##            return hash(self.__class__)
#
#        if not self._isreftime:
#            return hash(('Units', self._ut_unit))
#
##        return hash((self._ut_unit, self._rtime._jd0, self._rtime.calendar,
##                     self._rtime.tzoffset))
#        return hash(('Units', 
#                     self._ut_unit, self._rtime_jd0, self._rtime_calendar,
#                     self._rtime_tzoffset))
#    #--- End: def

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''
        if not self.isvalid:
            isvalid = ' (not valid)'
        else:
            isvalid = ''
            
        return '<CF {0}: {1}{2}>'.format(self.__class__.__name__, self, isvalid)
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        string = []
        if self._units is not None:
            string.append(self._units)
        if self._calendar is not None:
            string.append('{0}'.format(self._calendar))
        return ' '.join(string)
    #--- End: def

    def __deepcopy__(self, memo):
        '''

Used if copy.deepcopy is called on the variable.

'''
        return self
    #--- End: def

    def __nonzero__(self):
        '''

Truth value testing and the built-in operation ``bool``

x.__nonzero__() <==> x!=0

'''
        return self._ut_unit is not None
    #--- End: def

    def __eq__(self, other):
        '''

The rich comparison operator ``==``

x.__eq__(y) <==> x==y

'''
        return self.equals(other)
    #--- End: def

    def __ne__(self, other):
        '''

The rich comparison operator ``!=``

x.__ne__(y) <==> x!=y

'''
        return not self.equals(other)
    #--- End: def

    def __gt__(self, other):
        '''

The rich comparison operator ``>``

x.__gt__(y) <==> x>y

'''
        return self._comparison(other, '__gt__')
    #--- End: def

    def __ge__(self, other):
        '''

The rich comparison operator ````

x.__ge__(y) <==> x>y

'''
        return self._comparison(other, '__ge__')
    #--- End: def

    def ____(self, other):
        '''

The rich comparison operator ````

x.__lt__(y) <==> x<y

'''
        return self._comparison(other, '__lt__')
    #--- End: def

    def __le__(self, other):
        '''

The rich comparison operator ````

x.__le__(y) <==> x<=y

'''
        return self._comparison(other, '__le__')
    #--- End: def

    def __sub__(self, other):
        '''

The binary arithmetic operation ``-``

x.__sub__(y) <==> x-y

'''
        if (self._isreftime or
            (isinstance(other, self.__class__) and other._isreftime)):
            raise ValueError("Can't do %r - %r" % (self, other))

        try:
            _ut_unit = _ut_offset(self._ut_unit, _c_double(other))
            return type(self)(_ut_unit=_ut_unit)
        except:
            raise ValueError("Can't do %r - %r" % (self, other))
    #--- End: def

    def __add__(self, other):
        '''

The binary arithmetic operation ``+``

x.__add__(y) <==> x+y

'''
        if (self._isreftime or
            (isinstance(other, self.__class__) and other._isreftime)):
            raise ValueError("Can't do %r + %r" % (self, other))

        try:
            _ut_unit = _ut_offset(self._ut_unit, _c_double(-other))
            return type(self)(_ut_unit=_ut_unit)
        except:
            raise ValueError("Can't do %r + %r" % (self, other))
    #--- End: def

    def __mul__(self, other):
        '''

The binary arithmetic operation ``*``

x.__mul__(y) <==> x*y

'''
        if isinstance(other, self.__class__):
            if self._isreftime or other._isreftime:
                raise ValueError("Can't do %r * %r" % (self, other))

            try:
                ut_unit=_ut_multiply(self._ut_unit, other._ut_unit)
            except:
                raise ValueError("Can't do %r * %r" % (self, other))
            #--- End: try
        else:   
            if self._isreftime:
                raise ValueError("Can't do %r * %r" % (self, other))

            try:
                ut_unit=_ut_scale(_c_double(other), self._ut_unit)    
            except:
                raise ValueError("Can't do %r * %r" % (self, other))
        #--- End: if

        return type(self)(_ut_unit=ut_unit)
    #--- End: def

    def __div__(self, other):
        '''

x.__div__(y) <==> x/y

''' 
        if isinstance(other, self.__class__):
            if self._isreftime or other._isreftime:
                raise ValueError("Can't do %r / %r" % (self, other))

            try:
                ut_unit=_ut_divide(self._ut_unit, other._ut_unit)
            except:
                raise ValueError("Can't do %r / %r" % (self, other))
            #--- End: try
        else:
            if self._isreftime:
                raise ValueError("Can't do %r / %r" % (self, other))

            try:
                ut_unit=_ut_scale(_c_double(1.0/other), self._ut_unit)
            except:
                raise ValueError("Can't do %r / %r" % (self, other))
        #--- End: if

        return type(self)(_ut_unit=ut_unit)
    #--- End: def

    def __pow__(self, other, modulo=None):
        '''
The binary arithmetic operations ``**`` and ``pow``

x.__pow__(y) <==> x**y

'''
        # ------------------------------------------------------------
        # y must be either an integer or the reciprocal of a positive
        # integer.
        # ------------------------------------------------------------

        if modulo is not None:
            raise NotImplementedError(
                "3-argument power not supported for %r" %
                self.__class__.__name__)
        
        if self and not self._isreftime:
            ut_unit = self._ut_unit
            try:
                return type(self)(_ut_unit=_ut_raise(ut_unit, _c_int(other)))
            except:
                pass

            if 0 < other <= 1:
                # If other is a float and (1/other) is a positive
                # integer then take the (1/other)-th root. E.g. if
                # other is 0.125 then we take the 8-th root.
                try:
                    recip_other = 1/other
                    root        = int(recip_other)
                    if recip_other == root:
                        ut_unit = _ut_root(ut_unit, _c_int(root))
                        if ut_unit is not None:
                            return type(self)(_ut_unit=ut_unit)
                except:
                    pass
            else:
                # If other is a float equal to its integer tehn raise
                # to the integer part. E.g. if other is 3.0 then we
                # raise to the power of 3; if other is -2.0 then we
                # raise to the power of -2
                try:
                    root = int(other)
                    if other == root:
                        ut_unit = _ut_raise(ut_unit, _c_int(root))
                        if ut_unit is not None:
                            return type(self)(_ut_unit=ut_unit)
                except:
                    pass
            #--- End: if
        #--- End: if

        raise ValueError("Can't do %r ** %r" % (self, other))
    #--- End: def

    def __isub__(self, other):
        '''

x.__isub__(y) <==> x-=y

'''
        return self - other
    #--- End def

    def __iadd__(self, other):
        '''

x.__iadd__(y) <==> x+=y

'''
        return self + other
    #--- End def

    def __imul__(self, other):
        '''

The augmented arithmetic assignment ``*=``

x.__imul__(y) <==> x*=y

'''
        return self * other
    #--- End def

    def __idiv__(self, other):
        '''

The augmented arithmetic assignment ``/=``

x.__idiv__(y) <==> x/=y

'''
        return self.__div__(other)
    #--- End def

    def __ipow__(self, other):
        '''

The augmented arithmetic assignment ``**=``

x.__ipow__(y) <==> x**=y

'''
        return self ** other
    #--- End def

    def __rsub__(self, other):
        '''

The binary arithmetic operation ``-`` with reflected operands

x.__rsub__(y) <==> y-x

'''
        try:
            return -self + other
        except:
            raise ValueError("Can't do {0!r} - {1!r}".format(other, self))
    #--- End def

    def __radd__(self, other):
        '''

The binary arithmetic operation ``+`` with reflected operands

x.__radd__(y) <==> y+x

'''
        return self + other
    #--- End def

    def __rmul__(self, other):
        '''

The binary arithmetic operation ``*`` with reflected operands

x.__rmul__(y) <==> y*x

'''
        return self * other
    #--- End def

    def __rdiv__(self, other):
        '''

x.__rdiv__(y) <==> y/x

'''
        try:
            return (self ** -1) * other
        except:
            raise ValueError("Can't do %r / %r" % (other, self))
    #--- End def

    def __floordiv__(self, other):
        '''

x.__floordiv__(y) <==> x//y <==> x/y

'''
        return self.__div__(other)
    #--- End def

    def __ifloordiv__(self, other):
        '''

x.__ifloordiv__(y) <==> x//=y <==> x/=y

'''
        return self.__div__(other)
    #--- End def
 
    def __rfloordiv__(self, other):
        '''

x.__rfloordiv__(y) <==> y//x <==> y/x

'''
        try:
            return (self ** -1) * other
        except:
            raise ValueError("Can't do %r // %r" % (other, self))
    #--- End def

 
    def __truediv__(self, other):
        '''

x.__truediv__(y) <==> x/y

'''
        return self.__div__(other)
    #--- End def

    def __itruediv__(self, other):
        '''

x.__itruediv__(y) <==> x/=y

'''
        return self.__div__(other)
    #--- End def
 
    def __rtruediv__(self, other):
        '''

x.__rtruediv__(y) <==> y/x

'''    
        try:
            return (self ** -1) * other
        except:
            raise ValueError("Can't do %r / %r" % (other, self))
    #--- End def

    def __mod__(self, other):
        '''
    '''   
        raise ValueError("Can't do %r %% %r" % (self, other))
    #--- End def


    def __neg__(self):
        '''

The unary arithmetic operation ``-``

x.__neg__() <==> -x

'''
        return self * -1
    #--- End def

    def __pos__(self):
        '''

The unary arithmetic operation ``+``

x.__pos__() <==> +x

'''
        return self
    #--- End def

    def _comparison(self, other, method):
        '''
'''
        try:
            cv_converter = _ut_get_converter(self._ut_unit, other._ut_unit)
        except:
            raise ValueError(
"Units are not compatible: {0!r}, {1!r}".format(self, other))

        if not cv_converter:
            _cv_free(cv_converter)
            raise ValueError(
"Units are not compatible: {0!r}, {1!r}".format(self, other))

        y  = _c_double(1.0)
        pointer = ctypes.pointer(y)
        _cv_convert_doubles(cv_converter,
                            pointer,
                            _c_size_t(1),
                            pointer)
        _cv_free(cv_converter)

        return getattr(operator, method)(y.value, 1)
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def isreftime(self):
        '''

True if the units are reference time units, False otherwise.

Note that time units (such as ``'days'``) are not reference time
units.

.. seealso:: `isdimensionless`, `islongitude`,
             `islatitude`, `ispressure`, `istime`

:Examples:

>>> print Units('days since 2000-12-1 03:00').isreftime
True
>>> print Units('hours since 2100-1-1', calendar='noleap').isreftime
True
>>> print Units(calendar='360_day').isreftime
True
>>> print Units('days').isreftime
False
>>> print Units('kg').isreftime
False
>>> print Units().isreftime
False

'''
        return self._isreftime
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def message(self):
        '''

True if the units are reference time units, False otherwise.

Note that time units (such as ``'days'``) are not reference time
units.

.. seealso:: `isdimensionless`, `islongitude`,
             `islatitude`, `ispressure`, `istime`

:Examples:

>>> print Units('days since 2000-12-1 03:00').isreftime
True
>>> print Units('hours since 2100-1-1', calendar='noleap').isreftime
True
>>> print Units(calendar='360_day').isreftime
True
>>> print Units('days').isreftime
False
>>> print Units('kg').isreftime
False
>>> print Units().isreftime
False

'''
        return self._message
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def iscalendartime(self):
        '''True if the units are calendar time units, False otherwise.

Note that regular time units (such as ``'days'``) are not calendar
time units.

.. seealso:: `isdimensionless`, `islongitude`, `islatitude`,
             `ispressure`, `isreftime`, `istime`

:Examples:

>>> print Units('calendar_months').iscalendartime
True
>>> print Units('calendar_years').iscalendartime
True
>>> print Units('days').iscalendartime
False
>>> print Units('km s-1').iscalendartime
False
>>> print Units('kg').isreftime
False
>>> print Units('').isreftime
False
>>> print Units().isreftime
False

        '''
        return bool(_ut_are_convertible(self._ut_unit, _calendartime_ut_unit))
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def isdimensionless(self):
        '''
        
True if the units are dimensionless, false otherwise.

.. seealso:: `islongitude`, `islatitude`, `ispressure`, `isreftime`,
             `istime`

:Examples:

>>> cf.Units('').isdimensionless
True
>>> cf.Units('1').isdimensionless
True
>>> cf.Units('100').isdimensionless
True
>>> cf.Units('m/m').isdimensionless
True
>>> cf.Units('m km-1').isdimensionless
True
>>> cf.Units().isdimensionless
False
>>> cf.Units('m').isdimensionless
False
>>> cf.Units('m/s').isdimensionless
False
>>> cf.Units('days since 2000-1-1', calendar='noleap').isdimensionless
False

'''
        return bool(_ut_are_convertible(self._ut_unit, _dimensionless_unit_one))
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def ispressure(self):
        '''

True if the units are pressure units, false otherwise.

.. seealso:: `isdimensionless`, `islongitude`, `islatitude`,
             `isreftime`, `istime`

:Examples:

>>> Units('bar').ispressure
True
>>> Units('hPa').ispressure
True
>>> print Units('meter^-1-kilogram-second^-2').ispressure
True
>>> Units('hours since 2100-1-1', calendar='noleap').ispressure
False

'''
        ut_unit = self._ut_unit
        if ut_unit is None:
            return False
        
        return bool(_ut_are_convertible(ut_unit, _pressure_ut_unit))
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def islatitude(self):
        '''

True if and only if the units are latitude units.

This is the case if and only if the `units` attribute is one of
``'degrees_north'``, ``'degree_north'``, ``'degree_N'``,
``'degrees_N'``, ``'degreeN'``, and ``'degreesN'``.

Note that units of ``'degrees'`` are not latitude units.

.. seealso:: `isdimensionless`, `islongitude`, `ispressure`,
             `isreftime`, `istime`

:Examples:

>>> Units('degrees_north').islatitude
True
>>> Units('degrees').islatitude
False
>>> Units('degrees_east').islatitude
False
>>> Units('kg').islatitude
False
>>> Units().islatitude
False

'''
        return self._units in ('degrees_north', 'degree_north', 'degree_N',
                               'degrees_N', 'degreeN', 'degreesN')
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def islongitude(self):
        '''

True if and only if the units are longitude units.

This is the case if and only if the `units` attribute is one of
``'degrees_east'``, ``'degree_east'``, ``'degree_E'``,
``'degrees_E'``, ``'degreeE'``, and ``'degreesE'``.

Note that units of ``'degrees'`` are not longitude units.

.. seealso:: `isdimensionless`, `islatitude`, `ispressure`,
             `isreftime`, `istime`

:Examples:

>>> Units('degrees_east').islongitude
True
>>> Units('degrees').islongitude
False
>>> Units('degrees_north').islongitude
False
>>> Units('kg').islongitude
False
>>> Units().islongitude
False

'''
        return self._units in ('degrees_east', 'degree_east', 'degree_E',
                               'degrees_E', 'degreeE', 'degreesE')
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def istime(self):
        '''True if the units are time units, False otherwise.

Note that reference time units (such as ``'days since 2000-12-1'``)
are not time units, nor are calendar years and calendar months.

.. seealso:: `iscalendartime`, `isdimensionless`, `islongitude`,
             `islatitude`, `ispressure`, `isreftime`

:Examples:

>>> Units('days').istime
True
>>> Units('seconds').istime
True
>>> Units('kg').istime
False
>>> Units().istime
False
>>> Units('hours since 2100-1-1', calendar='noleap').istime
False
>>> Units(calendar='360_day').istime
False
>>> Units('calendar_years').istime
False
>>> Units('calendar_months').istime
False

        '''
        if self._isreftime:
            return False

        ut_unit = self._ut_unit
        if ut_unit is None:
            return False

        return bool(_ut_are_convertible(ut_unit, _day_ut_unit))
    #--- End: def
        ut_unit = self._ut_unit
        if ut_unit is None:
            return False
 
        return bool(_ut_are_convertible(ut_unit, _day_ut_unit))
    #--- End: def
 
    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def isvalid(self):
        '''Whether or not the units are valid.

**Examples:**

>>> v = Units('m/s')
>>> v.isvalid
True

>>> u = Units('M/S')
>>> u
<CF Units: M/S (not valid)>
>>> u.isvalid
False
>>> print(u)
'M/S'

        '''
        return getattr(self, '_isvalid', False)
    #--- End: def
    
    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def reftime(self):
        '''

The reference date-time of reference time units.

.. seealso:: `calendar`, `isreftime`, `units`

:Examples:

>>> repr(Units('days since 1900-1-1').reftime)
<CF Datetime: 1900-01-01 00:00:00>
>>> str(Units('days since 1900-1-1 03:00').reftime)
'1900-01-01 03:00:00'

'''    
        utime = self._utime
        if utime:
            origin = utime.origin
            if origin:
                return origin
        #--- End: if

        raise AttributeError(
            "{0!r} has no attribute 'reftime'".format(self))
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def calendar(self):
        '''
        
The calendar for reference time units.

May be any string allowed by the calendar CF property.

If it is unset then the default CF calendar is assumed when required.

.. seealso:: `units`

:Examples:

>>> Units(calendar='365_day').calendar
'365_day'
>>> Units('days since 2001-1-1', calendar='noleap').calendar
'noleap'
>>> Units('days since 2001-1-1').calendar
AttributeError: Units has no attribute 'calendar'

'''
        value = self._calendar
        if value is not None:
            return value

        raise AttributeError("%s has no attribute 'calendar'" %
                             self.__class__.__name__)    
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def units(self):
        '''

The units.

May be any string allowed by the units CF property.

.. seealso:: `calendar`

:Examples:

>>> Units('kg').units
'kg'
>>> Units('seconds').units
'seconds'
>>> Units('days since 2000-1-1', calendar='366_day').units
'days since 2000-1-1'

'''
        value = self._units
        if value is not None:
            return value

        raise AttributeError("'%s' object has no attribute 'units'" %
                             self.__class__.__name__)
    #--- End: def

    def equivalent(self, other):
        '''

Returns True if numeric values in one unit are convertible to numeric
values in the other unit.

.. seealso:: `~cf.Units.equals`

:Parameters:

    other : Units
        The other units.

:Returns:

    out : bool
        True if the units are equivalent, False otherwise.

:Examples:

>>> u = Units('m')
>>> v = Units('km')
>>> w = Units('s')

>>> u.equivalent(v)
True
>>> u.equivalent(w)
False

>>> u = Units('days since 2000-1-1')
>>> v = Units('days since 2000-1-1', calendar='366_day')
>>> w = Units('seconds since 1978-3-12', calendar='gregorian)

>>> u.equivalent(v)
False
>>> u.equivalent(w)
True

'''
        isreftime1 = self._isreftime
        isreftime2 = other._isreftime

        if isreftime1 and isreftime2:
            # Both units are reference-time units
            units0 = self._units
            units1 = other._units
            if units0 and units1 or (not units0 and not units1):
                return self._utime.calendar == other._utime.calendar
            else:
                return False
        #--- End: if

        # Still here? 
        if not self and not other:
            # Both units are null and therefore equivalent
            return True

        if not isreftime1 and not isreftime2:
            # Both units are not reference-time units
            return bool(_ut_are_convertible(self._ut_unit, other._ut_unit))
         
        # Still here? Then units are not equivalent.
        return False
    #--- End: def

    def formatted(self, names=None, definition=None):
        '''Formats the string stored in the `units` attribute in a standardized
manner. The `units` attribute is modified in place and its new value
is returned.

:Parameters:

    names: `bool`, optional
        Use unit names instead of symbols.

    definition: `bool`, optional
        The formatted string is given in terms of basic units instead
        of stopping any expansion at the highest level possible.

:Returns:

    out: `str` or `None`
        The formatted string. If the units have not yet been set, then
        `None` is returned.

:Examples:

>>> u = Units('W')
>>> u.units
'W'
>>> u.units = u.format(names=True)
>>> u.units
'watt'
>>> u.units = u.format(definition=True)
>>> u.units
'm2.kg.s-3'
>>> u.units = u.format(names=True, definition=True)
'meter^2-kilogram-second^-3'
>>> u.units = u.format()
>>> u.units
'W'

>>> u.units='dram'
>>> u.format(names=True)
'1.848345703125e-06 meter^3'

Formatting is also available during object initialization:

>>> u = Units('m/s', format=True)
>>> u.units
'm.s-1'

>>> u = Units('dram', names=True)
>>> u.units
'1.848345703125e-06 m3'

>>> u = Units('Watt')
>>> u.units
'Watt'

>>> u = Units('Watt', formatted=True)
>>> u.units
'W'

>>> u = Units('Watt', names=True)
>>> u.units
'watt'

>>> u = cf.Units('Watt', definition=True)
>>> u.units
'm2.kg.s-3'

>>> u = cf.Units('Watt', names=True, definition=True)
>>> u.units
'meter^2-kilogram-second^-3'

        '''
        ut_unit = self._ut_unit

        if ut_unit is None:
            return None
#            raise ValueError("Can't format unit {!r}".format(self))

        opts = _UT_ASCII
        if names:
            opts |= _UT_NAMES
        if definition:
            opts |= _UT_DEFINITION

        if _ut_format(ut_unit, _string_buffer, _sizeof_buffer, opts) != -1:
            out = _string_buffer.value
        else:
            raise ValueError("Can't format unit {!r}".format(self))

        if self.isreftime:
            out += ' since ' + self.reftime.strftime()

        return out
    #--- End: def

    @staticmethod
    def conform(x, from_units, to_units, inplace=False):
        '''

Conform values in one unit to equivalent values in another, compatible
unit. Returns the conformed values.

The values may either be a numpy array or a python numeric type. The
returned value is of the same type, except that input integers are
converted to floats (see the *inplace* keyword).

:Parameters:

    x : numpy.ndarray or python numeric

    from_units : Units
        The original units of `x`

    to_units : Units
        The units to which `x` should be conformed to.

    inplace : bool, optional
        If True and `x` is a numpy array then change it in place,
        creating no temporary copies, with one exception: If `x` is of
        integer type and the conversion is not null, then it will not
        be changed inplace and the returned conformed array will be of
        float type.

:Returns:

    out : numpy.ndarray or python numeric
        The modified numeric values.

:Examples:

>>> Units.conform(2, Units('km'), Units('m'))
2000.0

>>> import numpy
>>> a = numpy.arange(5.0)
>>> Units.conform(a, Units('minute'), Units('second'))
array([   0.,   60.,  120.,  180.,  240.])
>>> a
array([ 0.,  1.,  2.,  3.,  4.])

>>> Units.conform(a,
                  Units('days since 2000-12-1'),
                  Units('days since 2001-1-1'), inplace=True)
array([-31., -30., -29., -28., -27.])
>>> a
array([-31., -30., -29., -28., -27.])


.. warning::

   Do not change the calendar of reference time units in the current
   version. Whilst this is possible, it will almost certainly result
   in an incorrect interpretation of the data or an error. Allowing
   the calendar to be changed is under development and will be
   available soon.

'''
        if from_units.equals(to_units):
            if inplace:
                return x
            else:
                return x.copy()
        #--- End: if

        if not from_units.equivalent(to_units):
            raise ValueError("Units are not convertible: %r, %r" %
                             (from_units, to_units))

        ut_unit1 = from_units._ut_unit
        ut_unit2 = to_units._ut_unit

        if ut_unit1 is None or ut_unit2 is None:
            raise ValueError("Units are not convertible: %r, %r" %
                             (from_units, to_units))

        convert = _ut_compare(ut_unit1, ut_unit2)

        if from_units._isreftime and to_units._isreftime:
            # --------------------------------------------------------
            # Both units are time-reference units, so calculate the
            # non-zero offset in units of days.
            # --------------------------------------------------------
            offset = to_units._utime._jd0 - from_units._utime._jd0
        else:
            offset = 0

        # ----------------------------------------------------------------
        # If the two units are identical then no need to alter the
        # value, so return it unchanged.
        # ----------------------------------------------------------------
#        if not convert and not offset:
#            return x

        if convert:
            cv_converter = _ut_get_converter(ut_unit1, ut_unit2)
            if not cv_converter:
                _cv_free(cv_converter)
                raise ValueError("Units are not convertible: %r, %r" %
                                 (from_units, to_units))
        #-- End: if

        # ----------------------------------------------------------------
        # Find out if x is an numpy array or a python number
        # ----------------------------------------------------------------
        if isinstance(x, numpy_generic):
            # Convert a generic numpy scalar to a 0-d array
            x = numpy_array(x)

        if not isinstance(x, numpy_ndarray):
            x_is_numpy = False
        else:
            x_is_numpy = True

            if not x.flags.contiguous:
                x = numpy_array(x, order='C')
#ARRRGGHH dch

            # ----------------------------------------------------------------
            # Convert an integer numpy array to a float numpy array
            # ----------------------------------------------------------------
            if inplace:
                if x.dtype.kind is 'i':
                    if x.dtype.char is 'i':
                        y      = x.view(dtype='float32')
                        y[...] = x
                        x.dtype = numpy_dtype('float32')
                    elif x.dtype.char is 'l':
                        y      = x.view(dtype=float)
                        y[...] = x
                        x.dtype = numpy_dtype(float)
            else:
                # At numpy vn1.7 astype has many more keywords ...
                if x.dtype.kind is 'i':
                    if x.dtype.char is 'i':
                        x = x.astype('float32')
                    elif x.dtype.char is 'l':
                        x = x.astype(float)
                else:
                    x = x.copy()
        #--- End: if

        # ------------------------------------------------------------
        # Convert the array to the new units
        # ------------------------------------------------------------
        if convert:

            if x_is_numpy:
                # Create a pointer to the array cast to the appropriate
                # ctypes object
                itemsize = x.dtype.itemsize
                pointer  = x.ctypes.data_as(_ctypes_POINTER[itemsize])
#                print('U1 ', type(x))
                # Convert the array in place
                _cv_convert_array[itemsize](cv_converter,
                                            pointer,
                                            _c_size_t(x.size),
                                            pointer)
            else:
                # Create a pointer to the number cast to a ctypes double
                # object.
                y  = _c_double(x)
                pointer = ctypes.pointer(y)
                # Convert the pointer
                _cv_convert_doubles(cv_converter,
                                    pointer,
                                    _c_size_t(1),
                                    pointer)
                # Reset the number
                x = y.value
            #--- End: if

            _cv_free(cv_converter)
        #--- End: if
#        print('U', type(x))

        # ------------------------------------------------------------
        # Apply an offset for reference-time units
        # ------------------------------------------------------------
        if offset:
            # Convert the offset from 'days' to the correct units and
            # subtract it from x
            if _ut_compare(_day_ut_unit, ut_unit2):

                cv_converter = _ut_get_converter(_day_ut_unit, ut_unit2)
                scale   = numpy_array(1.0)
                pointer = scale.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
                _cv_convert_doubles(cv_converter,
                                    pointer,
                                    _c_size_t(scale.size),
                                    pointer)
                _cv_free(cv_converter)

                offset *= scale.item()
            #--- End: if

            x -= offset
        #--- End: if
#        print('U', type(x))
        return x
    #--- End: def

    def copy(self):
        '''

Return a deep copy.

Equivalent to ``copy.deepcopy(u)``.

:Returns:

    out :
        The deep copy.

:Examples:

>>> v = u.copy()

'''
        return self
    #--- End: def

    def dump(self, display=True, prefix=None, omit=()):
        '''

Return a string containing a description of the units.

:Parameters:
 
    display : bool, optional
        If False then return the description as a string. By default
        the description is printed, i.e. ``u.dump()`` is equivalent to
        ``print u.dump(display=False)``.

:Returns:

    out : None or str
        A string containing the description.

:Examples:

'''
        if prefix is None:
            prefix = self.__class__.__name__

        string = []

        for attr in self.__dict__:
            try:
                string.append("%s.%s = '%s'" % (prefix, attr,
                                                getattr(self, attr)))
            except AttributeError:
                pass
        #--- End: for

        string = '\n'.join(string)
       
        if display:
            print(string)
        else:
            return string
    #--- End: def

    def equals(self, other, rtol=None, atol=None):
        '''

Return True if and only if numeric values in one unit are convertible
to numeric values in the other unit and their conversion is a scale
factor of 1.

.. seealso:: `~cf.Units.equivalent`

:Parameters:

    other : Units
        The other units.

:Returns:

    out : bool
        True if the units are equal, False otherwise.

:Examples:

>>> u = Units('km')
>>> v = Units('1000m')
>>> w = Units('100000m')
>>> u.equals(v)
True
>>> u.equals(w)
False

>>> u = Units('m s-1')
>>> m = Units('m')
>>> s = Units('s')
>>> u.equals(m)
False
>>> u.equals(m/s)
True
>>> (m/s).equals(u)
True

Undefined units are considered equal:

>>> u = Units()
>>> v = Units()
>>> u.equals(v)
True

'''
        try:
            if _ut_compare(self._ut_unit, other._ut_unit):
                return False
        except AttributeError:
            return False

        isreftime1 = self._isreftime
        isreftime2 = other._isreftime

        if not isreftime1 and not isreftime2:
            # Neither units is reference-time so they're equal
            return True

        if isreftime1 and isreftime2:
            # Both units are reference-time
            utime0 = self._utime
            utime1 = other._utime
            if utime0.calendar != utime1.calendar:
                return False
            
            return utime0.origin_equals(utime1)
        #--- End: if

        # One unit is a reference-time and the other is not so they're
        # not equal
        return False
    #--- End: def

    def log(self, base):
        '''

Return the logarithmic unit corresponding to the given logarithmic
base.

:Parameters:

    base : int or float
        The logarithmic base.

:Returns:

    out : Units
        The logarithmic unit corresponding to the given logarithmic
        base.

:Examples:

>>> u = Units('W', names=True)
>>> u
<CF Units: watt>

>>> u.log(10)
<CF Units: lg(re 1 W)>
>>> u.log(2)
<CF Units: lb(re 1 W)>

>>> import math
>>> u.log(math.e)
<CF Units: ln(re 1 W)>

>>> u.log(3.5)
<CF Units: 0.798235600147928 ln(re 1 W)>

'''
        try:
            _ut_unit = _ut_log(_c_double(base), self._ut_unit)
        except TypeError:
            pass
        else:
            if _ut_unit:
                return type(self)(_ut_unit=_ut_unit)
        #--- End: try

        raise ValueError(
            "Can't take the logarithm to the base %r of %r" % (base, self))
    #--- End def

#--- End: class


# ====================================================================
#
# Utime object
#
# ====================================================================
if netCDF4.__version__ < '1.4':
    Parent = netCDF4.netcdftime.utime
else:
    Parent = cftime.utime

class Utime(Parent):
    '''

Performs conversions of netCDF time coordinate data to/from datetime
objects.

This object is (currently) functionally equivalent to a
`netCDF4.netcdftime.utime` object.

**Attributes**

==============  ======================================================
Attribute       Description
==============  ======================================================
`!_jd0`         
`!calendar`     The calendar used in the time calculation.
`!origin`       A date/time object for the reference time.
`!tzoffset`     Time zone offset in minutes.
`!unit_string`  
`!units`        
==============  ======================================================

'''
    def __init__(self, calendar, unit_string=None):
        '''

**Initialization**

:Parameters:

    calendar : str
        The calendar used in the time calculations. Must be one of:
        ``'gregorian'``, ``'360_day'``, ``'365_day'``, ``'366_day'``,
        ``'julian'``, ``'proleptic_gregorian'``, although this is not
        checked.

    unit_string : str, optional
        A string of the form "time-units since <time-origin>"
        defining the reference-time units.

'''
        if unit_string:
#            try:
            _netCDF4_netcdftime_utime.__init__(self, unit_string, calendar)
#            except ValueError:
#                #
#                pass
        else:
            self.calendar    = calendar
            self._jd0        = None
            self.origin      = None
            self.tzoffset    = None
            self.unit_string = None
            self.units       = None
    #--- End: def

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''
        unit_string = self.unit_string
        if unit_string:
            x = [unit_string]
        else:
            x = []

        x.append(self.calendar)

        return "<CF Utime: %s>" % ' '.join(x)
    #--- End: def 

    def num2date(self, time_value):
        '''Return a datetime-like object given a time value.

The units of the time value are described by the `!unit_string` and
`!calendar` attributes.

See `netCDF4.netcdftime.utime.num2date` for details.

In addition to `netCDF4.netcdftime.utime.num2date`, this method
handles units of months and years as defined by Udunits, ie. 1 year =
365.242198781 days, 1 month = 365.242198781/12 days.

        '''
        units = self.units
        unit_string = self.unit_string

        if units in ('month', 'months'):
            # Convert months to days
            unit_string = unit_string.replace(units, 'days', 1)
            time_value = numpy_array(time_value)*365.242198781/12
        elif units in ('year', 'years', 'yr'):
            # Convert years to days
            unit_string = unit_string.replace(units, 'days', 1)
            time_value = numpy_array(time_value)*365.242198781

        u = _netCDF4_netcdftime_utime(unit_string, self.calendar)        

        return u.num2date(time_value)
    #--- End: def

    def origin_equals(self, other):

        '''

'''
        if self is other:
            return True
        else:
            return (self._jd0     == other._jd0     and
                    self.calendar == other.calendar and
                    self.tzoffset == other.tzoffset)
    #--- End: def

#--- End: class
