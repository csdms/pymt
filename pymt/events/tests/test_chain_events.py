from pytest import approx

from pymt.events.chain import ChainEvent
from pymt.events.manager import EventManager
from pymt.events.port import PortEvent
from pymt.framework.services import get_component_instance


def assert_port_value_equal(port, name, value):
    assert port.get_value(name) == approx(value)


def test_length_zero():
    foo = ChainEvent([])

    with EventManager(((foo, 1.),)) as mngr:
        assert mngr.time == approx(0.)

        mngr.run(2.)
        assert mngr.time == approx(2.)


def test_length_one(with_earth_and_air):
    air = get_component_instance("air_port")
    foo = ChainEvent([PortEvent(port=air)])

    with EventManager(((foo, 1.),)) as mngr:
        assert_port_value_equal(air, "air__density", 0.)
        mngr.run(2.)
        assert_port_value_equal(air, "air__density", 2.)

    assert_port_value_equal(air, "air__density", 0.)


def test_length_two(with_earth_and_air):
    air = get_component_instance("air_port")
    earth = get_component_instance("earth_port")

    foo = ChainEvent([PortEvent(port=air), PortEvent(port=earth)])

    with EventManager([(foo, 1.2)]) as mngr:
        assert_port_value_equal(earth, "earth_surface__temperature", 0.)
        assert_port_value_equal(air, "air__density", 0.)

        mngr.run(1.)
        assert_port_value_equal(earth, "earth_surface__temperature", 0.)
        assert_port_value_equal(air, "air__density", 0.)

        mngr.run(2.)
        assert_port_value_equal(earth, "earth_surface__temperature", 1.2)
        assert_port_value_equal(air, "air__density", 1.2)


def test_repeated_events(with_earth_and_air):
    air = get_component_instance("air_port")
    earth = get_component_instance("earth_port")

    foo = ChainEvent([PortEvent(port=air), PortEvent(port=earth), PortEvent(port=air)])

    with EventManager([(foo, 1.2)]) as mngr:
        assert_port_value_equal(earth, "earth_surface__temperature", 0.)
        assert_port_value_equal(air, "air__density", 0.)

        mngr.run(1.)
        assert_port_value_equal(earth, "earth_surface__temperature", 0.)
        assert_port_value_equal(air, "air__density", 0.)

        mngr.run(2.)
        assert_port_value_equal(earth, "earth_surface__temperature", 1.2)
        assert_port_value_equal(air, "air__density", 1.2)
