import os
import numpy as np
from numpy.testing import assert_array_equal
from nose.tools import assert_equal, assert_false, assert_almost_equal

from cmt.events.manager import EventManager
from cmt.events.port import PortMapEvent, PortEvent
from cmt.events.chain import ChainEvent
from cmt.testing.assertions import assert_isfile_and_remove

from cmt.testing import services


def assert_port_value_equal(port, name, value):
    assert_array_equal(port.get_grid_values(name), value)


def test_length_zero():
    foo = ChainEvent([])

    with EventManager(((foo, 1.), )) as mngr:
        assert_equal(mngr.time, 0.)

        mngr.run(2.)
        assert_equal(mngr.time, 2.)


def test_length_one():
    air = services.get_port('air_port')
    foo = ChainEvent([PortEvent(port=air), ])

    with EventManager(((foo, 1.), )) as mngr:
        assert_port_value_equal(air, 'air__density', 0.)
        mngr.run(2.)
        assert_port_value_equal(air, 'air__density', 2.)

    assert_port_value_equal(air, 'air__density', 0.)


def test_length_two():
    air = services.get_port('air_port')
    earth = services.get_port('earth_port')

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
    air = services.get_port('air_port')
    earth = services.get_port('earth_port')

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
