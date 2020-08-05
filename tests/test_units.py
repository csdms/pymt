import os
import random

import numpy as np
import pytest

from pymt.units import transform_azimuth_to_math, transform_math_to_azimuth


from pymt import UnitSystem
from pymt._udunits2 import UnitNameError, UnitStatus
from pymt.errors import IncompatibleUnitsError


@pytest.fixture
def system():
    os.environ.pop("UDUNITS2_XML_PATH", None)
    return UnitSystem()


def test_get_xml():
    os.environ.pop("UDUNITS2_XML_PATH", None)
    path, status = UnitSystem.get_xml_path()
    assert path.is_file()
    assert status == UnitStatus.OPEN_DEFAULT

    path, status = UnitSystem.get_xml_path(path)
    assert path.is_file()
    assert status == UnitStatus.OPEN_ARG

    os.environ["UDUNITS2_XML_PATH"] = str(path)
    path, status = UnitSystem.get_xml_path()
    assert path.is_file()
    assert status == UnitStatus.OPEN_ENV


def test_default_system():
    os.environ.pop("UDUNITS2_XML_PATH", None)
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


def test_env_system(system):
    os.environ["UDUNITS2_XML_PATH"] = str(system.database)
    env_system = UnitSystem()

    assert env_system.status == "env"
    assert env_system.database.is_file()
    assert str(env_system) == str(system)
    assert env_system.database.samefile(system.database)
    assert env_system == system


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


@pytest.mark.parametrize(
    ("lhs", "cmp_", "rhs"), [
        ("m", "lt", "km"),
        ("m", "le", "km"),
        ("m", "le", "m"),
        ("m", "eq", "m"),
        ("m", "ne", "km"),
        ("km", "ge", "m"),
        ("km", "ge", "km"),
        ("km", "gt", "m"),
    ]
)
def test_unit_comparisons(system, lhs, cmp_, rhs):
    compare = getattr(system.Unit(lhs), f"__{cmp_}__")
    assert compare(system.Unit(rhs))
    with pytest.raises(TypeError):
        compare(rhs)


def test_unit_symbol(system):
    meters = system.Unit("m")
    assert meters.symbol == "m"

    km = system.Unit("km")
    assert km.symbol is None


def test_unit_name(system):
    meters = system.Unit("m")
    assert meters.name == "meter"

    km = system.Unit("km")
    assert km.name is None


def test_unit_is_dimensionless(system):
    assert not system.Unit("m").is_dimensionless
    assert system.Unit("1").is_dimensionless
    assert system.Unit("rad").is_dimensionless


def test_unit_is_convertible(system):
    assert system.Unit("m").is_convertible_to(system.Unit("km"))
    assert not system.Unit("m").is_convertible_to(system.Unit("kg"))

    with pytest.raises(TypeError):
        system.Unit("m").is_convertible_to("km")


def test_unit_converter_length(system):
    meters = system.Unit("m")
    km = system.Unit("km")

    assert meters.to(km)(1.0) == pytest.approx(1e-3)
    with pytest.raises(TypeError):
        meters.to("km")

    m_to_km = meters.to(km)
    assert m_to_km(1.0) == pytest.approx(1e-3)


def test_unit_converter_time(system):
    hours = system.Unit("h")
    seconds = system.Unit("s")
    hours_to_seconds = hours.to(seconds)
    assert hours_to_seconds(1.0) == pytest.approx(3600.0)

    with pytest.raises(TypeError):
        hours.to("s")


def test_unit_converter_same_units(system):
    hours = system.Unit("h")
    hours_to_hours = hours.to(system.Unit("h"))
    assert hours_to_hours(1.0) == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("to_", "from_"),
    [("not_a_unit", "m"), ("m", "not_a_unit"), ("not_a_unit", "not_a_unit")],
)
def test_unit_converter_bad_from_units(system, to_, from_):
    with pytest.raises(UnitNameError):
        system.Unit(from_).to(system.Unit(to_))


def test_unit_converter_incompatible_units(system):
    with pytest.raises(IncompatibleUnitsError):
        system.Unit("s").to(system.Unit("m"))


def test_unit_converter_inverse(system):
    val = random.random()
    seconds_to_hours = system.Unit("s").to(system.Unit("h"))
    hours_to_seconds = system.Unit("h").to(system.Unit("s"))
    assert hours_to_seconds(seconds_to_hours(val)) == pytest.approx(val)


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
