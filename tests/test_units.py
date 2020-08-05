import os
import random
import pathlib

import numpy as np
import pytest

from pymt.units import transform_azimuth_to_math, transform_math_to_azimuth


from pymt import UnitSystem
from pymt._udunits2 import UnitNameError
from pymt.errors import IncompatibleUnitsError


@pytest.fixture
def system():
    return UnitSystem()


def test_default_system():
    system = UnitSystem()
    assert system.status == "default"
    assert system.database.is_file()


def test_user_system():
    path = UnitSystem().database
    system = UnitSystem(path)
    assert system.status == "user"
    assert system.database.is_file()
    assert system == UnitSystem()
    assert UnitSystem(path) == UnitSystem(str(path))


def test_env_system():
    os.environ.pop("UDUNITS2_XML_PATH", None)
    default_system = UnitSystem()
    os.environ["UDUNITS2_XML_PATH"] = str(default_system.database)
    system = UnitSystem()
    os.environ.pop("UDUNITS2_XML_PATH")

    assert system.status == "env"
    assert system.database.is_file()
    assert str(system) == str(default_system)
    assert system.database.samefile(default_system.database)
    assert system == default_system


def test_system_dimensionless(system):
    assert system.dimensionless_unit() == system.Unit("1")
    assert str(system.dimensionless_unit()) == "1"


def test_system_unit_by_name(system):
    assert system.unit_by_name("meter") == system.Unit("m")
    assert system.unit_by_name("meters") == system.Unit("m")
    assert system.unit_by_name("m") is None
    assert system.unit_by_name("meter2") is None
    assert system.unit_by_name("not_a_name") is None


def test_system_unit_by_symbol(system):
    assert system.unit_by_symbol("m") == system.Unit("m")
    assert system.unit_by_symbol("km") is None
    assert system.unit_by_symbol("meter") is None
    assert system.unit_by_symbol("m s-2") is None
    assert system.unit_by_symbol("not_a_symbol") is None


def test_unit_converter_length(system):
    meters = system.Unit("m")
    assert meters.to("km")(1.0) == pytest.approx(1e-3)
    # assert meters.convert_to(1.0, "km") == pytest.approx(1e-3)

    m_to_km = meters.to("km")
    # convert = UnitConverter("m", "km")
    assert m_to_km(1.0) == pytest.approx(1e-3)


def test_unit_converter_time(system):
    hours = system.Unit("h")
    hours_to_seconds = hours.to("s")
    assert hours_to_seconds(1.0) == pytest.approx(3600.0)


def test_unit_converter_same_units(system):
    hours = system.Unit("h")
    hours_to_hours = hours.to("h")
    assert hours_to_hours(1.0) == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("to_", "from_"),
    [("not_a_unit", "m"), ("m", "not_a_unit"), ("not_a_unit", "not_a_unit")],
)
def test_unit_converter_bad_from_units(system, to_, from_):
    with pytest.raises(UnitNameError):
        system.Unit(from_).to(to_)


def test_unit_converter_incompatible_units(system):
    with pytest.raises(IncompatibleUnitsError):
        system.Unit("s").to("m")


def test_unit_converter_inverse(system):
    val = random.random()
    seconds_to_hours = system.Unit("s").to("h")
    hours_to_seconds = system.Unit("h").to("s")
    assert hours_to_seconds(seconds_to_hours(val)) == pytest.approx(val)


# def test_unit_converter_units_attr(system):
#     m_to_km = system.Unit("m").to("km")
#     assert m_to_km.src_units == "m"
#     assert m_to_km.dst_units == "km"


def test_math_to_azimuth():
    angle = transform_math_to_azimuth(np.pi * 0.5, "rad")
    assert angle == pytest.approx(0.0)


def test_math_to_azimuth_inplace():
    x = np.array([0.0, 0.5, 1.0, 1.5]) * np.pi
    angle = transform_math_to_azimuth(x, "rad")
    assert angle is x
    assert angle == pytest.approx([np.pi * 0.5, 0.0, -np.pi * 0.5, -np.pi])


def test_azimuth_to_math():
    angle = transform_azimuth_to_math(0.0, "rad")
    assert angle == pytest.approx(np.pi * 0.5)


def test_azimuth_to_math_inplace():
    x = np.array([np.pi * 0.5, 0.0, -np.pi * 0.5, -np.pi])
    angle = transform_azimuth_to_math(x, "rad")
    assert angle is x
    assert angle == pytest.approx([0.0, np.pi * 0.5, np.pi, np.pi * 1.5])
