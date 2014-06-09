from numpy.testing import assert_array_equal
from nose.tools import assert_equal

from cmt.events.manager import EventManager
from cmt.events.port import PortEvent
from cmt.events.chain import ChainEvent
from cmt.framework.services import get_component_instance


def assert_port_value_equal(port, name, value):
    assert_array_equal(port.get_grid_values(name), value)


def test_length_zero():
    foo = ChainEvent([])

    with EventManager(((foo, 1.), )) as mngr:
        assert_equal(mngr.time, 0.)

        mngr.run(2.)
        assert_equal(mngr.time, 2.)


def test_length_one():
    air = get_component_instance('air_port')
    foo = ChainEvent([PortEvent(port=air), ])

    with EventManager(((foo, 1.), )) as mngr:
        assert_port_value_equal(air, 'air__density', 0.)
        mngr.run(2.)
        assert_port_value_equal(air, 'air__density', 2.)

    assert_port_value_equal(air, 'air__density', 0.)


def test_length_two():
    air = get_component_instance('air_port')
    earth = get_component_instance('earth_port')

    foo = ChainEvent([PortEvent(port=air), PortEvent(port=earth)])

    with EventManager([(foo, 1.2), ]) as mngr:
        assert_port_value_equal(earth, 'earth_surface__temperature', 0.)
        assert_port_value_equal(air, 'air__density', 0.)

        mngr.run(1.)
        assert_port_value_equal(earth, 'earth_surface__temperature', 0.)
        assert_port_value_equal(air, 'air__density', 0.)

        mngr.run(2.)
        assert_port_value_equal(earth, 'earth_surface__temperature', 1.2)
        assert_port_value_equal(air, 'air__density', 1.2)


def test_repeated_events():
    air = get_component_instance('air_port')
    earth = get_component_instance('earth_port')

    foo = ChainEvent([PortEvent(port=air), PortEvent(port=earth),
                      PortEvent(port=air)])

    with EventManager([(foo, 1.2), ]) as mngr:
        assert_port_value_equal(earth, 'earth_surface__temperature', 0.)
        assert_port_value_equal(air, 'air__density', 0.)

        mngr.run(1.)
        assert_port_value_equal(earth, 'earth_surface__temperature', 0.)
        assert_port_value_equal(air, 'air__density', 0.)

        mngr.run(2.)
        assert_port_value_equal(earth, 'earth_surface__temperature', 1.2)
        assert_port_value_equal(air, 'air__density', 1.2)
