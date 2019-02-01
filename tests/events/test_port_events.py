import numpy as np
from pytest import approx

from pymt.events.manager import EventManager
from pymt.events.port import PortEvent


def assert_port_value_equal(port, name, value):
    assert port.get_value(name) == approx(value)


def test_one_event(tmpdir, with_earth_and_air):
    with tmpdir.as_cwd():
        foo = PortEvent(port="air_port")

        with EventManager(((foo, 1.0),)) as mngr:
            assert_port_value_equal(foo._port, "air__density", 0.0)

            mngr.run(1.0)
            assert_port_value_equal(foo._port, "air__density", 1.0)

            mngr.run(1.0)
            assert_port_value_equal(foo._port, "air__density", 1.0)

            for time in np.arange(1.0, 2.0, 0.1):
                mngr.run(time)
            assert_port_value_equal(foo._port, "air__density", 1.0)

            mngr.run(2.0)
            assert_port_value_equal(foo._port, "air__density", 2.0)

            for time in np.arange(2.0, 5.0, 0.1):
                mngr.run(time)
            assert mngr.time == approx(4.9)
            assert_port_value_equal(foo._port, "air__density", 4.0)

        assert_port_value_equal(foo._port, "air__density", 0.0)


def test_two_events(tmpdir, with_earth_and_air):
    with tmpdir.as_cwd():
        foo = PortEvent(port="air_port")
        bar = PortEvent(port="earth_port")

        with EventManager(((foo, 1.0), (bar, 1.2))) as mngr:
            assert_port_value_equal(foo._port, "air__density", 0.0)
            assert_port_value_equal(bar._port, "earth_surface__temperature", 0.0)

            mngr.run(1.0)
            assert_port_value_equal(foo._port, "air__density", 1.0)
            assert_port_value_equal(bar._port, "earth_surface__temperature", 0.0)

            mngr.run(1.0)
            assert_port_value_equal(foo._port, "air__density", 1.0)
            assert_port_value_equal(bar._port, "earth_surface__temperature", 0.0)

            mngr.run(1.3)
            assert_port_value_equal(foo._port, "air__density", 1.0)
            assert_port_value_equal(bar._port, "earth_surface__temperature", 1.2)

            mngr.run(2.0)
            assert_port_value_equal(foo._port, "air__density", 2.0)
            assert_port_value_equal(bar._port, "earth_surface__temperature", 1.2)

            for time in np.arange(2.0, 5.0, 0.1):
                mngr.run(time)
            assert mngr.time == approx(4.9)
            assert_port_value_equal(foo._port, "air__density", 4.0)
            assert_port_value_equal(bar._port, "earth_surface__temperature", 4.8)

        assert_port_value_equal(foo._port, "air__density", 0.0)
        assert_port_value_equal(bar._port, "earth_surface__temperature", 0.0)
