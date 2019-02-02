#! /usr/bin/env python
import os

import pytest
import xarray

from pymt.portprinter.port_printer import PortPrinter


def test_one_printer(tmpdir, with_two_components):
    with tmpdir.as_cwd():
        queue = PortPrinter.from_string(
            """
[print.ocean_surface__temperature]
format=nc
port=water_port
"""
        )
        assert isinstance(queue, PortPrinter)

        queue.open()
        queue.write()

        assert os.path.isfile("ocean_surface__temperature.nc")


def test_multiple_printers(tmpdir, with_two_components):
    with tmpdir.as_cwd():
        queue = PortPrinter.from_string(
            """
[print.air__density]
format=nc
port=air_port

[print.glacier_top_surface__slope]
format=nc
port=earth_port
"""
        )

        assert isinstance(queue, list)

        for printer in queue:
            printer.open()

        for _ in range(5):
            for printer in queue:
                printer.write()

        assert os.path.isfile("air__density.nc")
        ds = xarray.open_dataset("air__density.nc")
        assert "air__density" in ds.variables
        assert ds.dims["time"] == 5

        assert os.path.isfile("glacier_top_surface__slope.nc")
        ds = xarray.open_dataset("glacier_top_surface__slope.nc")
        assert "glacier_top_surface__slope" in ds.variables
        assert ds.dims["time"] == 5
