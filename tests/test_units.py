import random

import numpy as np
from pytest import approx, raises

from pymt.units import (
    UnitConverter,
    transform_azimuth_to_math,
    transform_math_to_azimuth,
)


def test_unit_converter_length():
    convert = UnitConverter("m")
    assert convert(1.0, "km") == approx(1e-3)


def test_unit_converter_time():
    convert = UnitConverter("h")
    assert convert(1.0, "s") == approx(3600.0)


def test_unit_converter_same_units():
    convert = UnitConverter("h")
    assert convert(1.0, "h") == approx(1.0)


def test_unit_converter_bad_from_units():
    with raises(ValueError):
        UnitConverter("not-a-unit")


def test_unit_converter_incompatible_units():
    convert = UnitConverter("s")
    with raises(ValueError):
        convert(1.0, "m")


def test_unit_converter_inverse():
    val = random.random()
    convert = UnitConverter("s")
    assert convert.inv(convert(val, "h"), "h") == approx(val)


def test_unit_converter_units_attr():
    convert = UnitConverter("m")
    assert isinstance(convert.units, str)
    assert convert.units == "m"


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
