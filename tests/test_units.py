import random

import numpy as np
from pytest import approx, mark, raises

from pymt.units import (
    # UnitConverter,
    transform_azimuth_to_math,
    transform_math_to_azimuth,
)

from pymt.udunits2 import Unit, UnitConverter
from pymt.errors import BadUnitError, IncompatibleUnitsError


def test_unit_converter_length():
    meters = Unit("m")
    assert meters.convert_to(1.0, "km") == approx(1e-3)

    convert = UnitConverter("m", "km")
    assert convert(1.0) == approx(1e-3)


def test_unit_converter_time():
    convert = UnitConverter("h", "s")
    assert convert(1.0) == approx(3600.0)


def test_unit_converter_same_units():
    convert = UnitConverter("h", "h")
    assert convert(1.0) == approx(1.0)


@mark.parametrize(
    ("to_", "from_"),
    [("not_a_unit", "m"), ("m", "not_a_unit"), ("not_a_unit", "not_a_unit")],
)
def test_unit_converter_bad_from_units(to_, from_):
    with raises(BadUnitError):
        UnitConverter(to_, from_)


def test_unit_converter_incompatible_units():
    with raises(IncompatibleUnitsError):
        UnitConverter("s", "m")


def test_unit_converter_inverse():
    val = random.random()
    convert = UnitConverter("s", "h")
    assert convert(convert(val), inverse=True) == approx(val)


def test_unit_converter_units_attr():
    convert = UnitConverter("m", "km")
    assert convert.src_units == "m"
    assert convert.dst_units == "km"


def test_math_to_azimuth():
    angle = transform_math_to_azimuth(np.pi * 0.5, "rad")
    assert angle == approx(0.0)


def test_math_to_azimuth_inplace():
    x = np.array([0.0, 0.5, 1.0, 1.5]) * np.pi
    angle = transform_math_to_azimuth(x, "rad")
    assert angle is x
    assert angle == approx([np.pi * 0.5, 0.0, -np.pi * 0.5, -np.pi])


def test_azimuth_to_math():
    angle = transform_azimuth_to_math(0.0, "rad")
    assert angle == approx(np.pi * 0.5)


def test_azimuth_to_math_inplace():
    x = np.array([np.pi * 0.5, 0.0, -np.pi * 0.5, -np.pi])
    angle = transform_azimuth_to_math(x, "rad")
    assert angle is x
    assert angle == approx([0.0, np.pi * 0.5, np.pi, np.pi * 1.5])
