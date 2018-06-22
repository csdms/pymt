import os
import numpy as np
from nose.tools import assert_equal, assert_false

from pymt.events.manager import EventManager
from pymt.events.printer import PrintEvent
from pymt.testing.assertions import assert_isfile_and_remove


def test_one_event():
    foo = PrintEvent(port="air_port", name="air__density", format="vtk")

    with EventManager(((foo, 1.),)) as mngr:
        assert_equal(mngr.time, 0.)

        mngr.run(1.)
        assert_equal(mngr.time, 1.)

        mngr.run(1.)
        assert_equal(mngr.time, 1.)

        for time in np.arange(1., 2., .1):
            mngr.run(time)
            assert_equal(mngr.time, time)

        mngr.run(2.)
        assert_equal(mngr.time, 2.)

        for time in np.arange(2., 5., .1):
            mngr.run(time)
            assert_equal(mngr.time, time)

    assert_isfile_and_remove("air__density_0000.vtu")
    assert_isfile_and_remove("air__density_0001.vtu")
    assert_isfile_and_remove("air__density_0002.vtu")
    assert_isfile_and_remove("air__density_0003.vtu")


def test_two_events():
    foo = PrintEvent(port="air_port", name="air__density", format="vtk")
    bar = PrintEvent(port="air_port", name="air__temperature", format="vtk")

    with EventManager(((foo, 1.), (bar, 1.2))) as mngr:
        mngr.run(1.)
        assert_isfile_and_remove("air__density_0000.vtu")

        mngr.run(2.)
        assert_isfile_and_remove("air__density_0001.vtu")
        assert_isfile_and_remove("air__temperature_0000.vtu")
        assert_equal(mngr.time, 2.)

        mngr.run(5.)
        assert_equal(mngr.time, 5.)

    assert_isfile_and_remove("air__density_0002.vtu")
    assert_isfile_and_remove("air__density_0003.vtu")
    assert_isfile_and_remove("air__density_0004.vtu")
    assert_false(os.path.exists("air__density_0005.vtu"))

    assert_isfile_and_remove("air__temperature_0001.vtu")
    assert_isfile_and_remove("air__temperature_0002.vtu")
    assert_isfile_and_remove("air__temperature_0003.vtu")
    assert_false(os.path.exists("air__temperature_0004.vtu"))
