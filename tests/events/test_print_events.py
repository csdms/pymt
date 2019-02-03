import os

import numpy as np
from pytest import approx

from pymt.events.manager import EventManager
from pymt.events.printer import PrintEvent


def test_one_event(tmpdir, with_earth_and_air):
    with tmpdir.as_cwd():
        foo = PrintEvent(port="air_port", name="air__density", format="netcdf")

        with EventManager(((foo, 1.0),)) as mngr:
            assert mngr.time == approx(0.0)

            mngr.run(1.0)
            assert mngr.time == approx(1.0)

            mngr.run(1.0)
            assert mngr.time == approx(1.0)

            for time in np.arange(1.0, 2.0, 0.1):
                mngr.run(time)
                assert mngr.time == approx(time)

            mngr.run(2.0)
            assert mngr.time == approx(2.0)

            for time in np.arange(2.0, 5.0, 0.1):
                mngr.run(time)
                assert mngr.time == approx(time)

        assert os.path.isfile("air__density.nc")
        # assert os.path.isfile("air__density_0001.vtu")
        # assert os.path.isfile("air__density_0002.vtu")
        # assert os.path.isfile("air__density_0003.vtu")


def test_two_events(tmpdir, with_earth_and_air):
    with tmpdir.as_cwd():
        foo = PrintEvent(port="air_port", name="air__density", format="nc")
        bar = PrintEvent(port="air_port", name="air__temperature", format="nc")

        with EventManager(((foo, 1.0), (bar, 1.2))) as mngr:
            mngr.run(1.0)
            assert os.path.isfile("air__density.nc")

            mngr.run(2.0)
            assert os.path.isfile("air__temperature.nc")
            assert mngr.time == approx(2.0)

            mngr.run(5.0)
            assert mngr.time == approx(5.0)
