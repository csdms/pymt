import numpy as np
from numpy.testing import assert_array_equal
from pytest import approx

from pymt.events.manager import EventManager
from pymt.events.port import PortEvent


def assert_port_value_equal(port, name, value):
    assert port.get_value(name) == approx(value)


def test_one_event(with_earth_and_air):
    foo = PortEvent(port="air_port")

    with EventManager(((foo, 1.),)) as mngr:
        assert_port_value_equal(foo._port, "air__density", 0.)

        mngr.run(1.)
        assert_port_value_equal(foo._port, "air__density", 1.)

        mngr.run(1.)
        assert_port_value_equal(foo._port, "air__density", 1.)

        for time in np.arange(1., 2., .1):
            mngr.run(time)
        assert_port_value_equal(foo._port, "air__density", 1.)

        mngr.run(2.)
        assert_port_value_equal(foo._port, "air__density", 2.)

        for time in np.arange(2., 5., .1):
            mngr.run(time)
        assert mngr.time == approx(4.9)
        assert_port_value_equal(foo._port, "air__density", 4.)

    assert_port_value_equal(foo._port, "air__density", 0.)


def test_two_events(with_earth_and_air):
    foo = PortEvent(port="air_port")
    bar = PortEvent(port="earth_port")

    with EventManager(((foo, 1.), (bar, 1.2))) as mngr:
        assert_port_value_equal(foo._port, "air__density", 0.)
        assert_port_value_equal(bar._port, "earth_surface__temperature", 0.)

        mngr.run(1.)
        assert_port_value_equal(foo._port, "air__density", 1.)
        assert_port_value_equal(bar._port, "earth_surface__temperature", 0.)

        mngr.run(1.)
        assert_port_value_equal(foo._port, "air__density", 1.)
        assert_port_value_equal(bar._port, "earth_surface__temperature", 0.)

        mngr.run(1.3)
        assert_port_value_equal(foo._port, "air__density", 1.)
        assert_port_value_equal(bar._port, "earth_surface__temperature", 1.2)

        mngr.run(2.)
        assert_port_value_equal(foo._port, "air__density", 2.)
        assert_port_value_equal(bar._port, "earth_surface__temperature", 1.2)

        for time in np.arange(2., 5., .1):
            mngr.run(time)
        assert mngr.time == approx(4.9)
        assert_port_value_equal(foo._port, "air__density", 4.)
        assert_port_value_equal(bar._port, "earth_surface__temperature", 4.8)

    assert_port_value_equal(foo._port, "air__density", 0.)
    assert_port_value_equal(bar._port, "earth_surface__temperature", 0.)
