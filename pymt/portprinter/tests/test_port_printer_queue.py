#! /usr/bin/env python
import os

from six.moves import xrange

from pymt.portprinter.port_printer import PortPrinter


def test_one_printer(tmpdir, with_two_components):
    with tmpdir.as_cwd():
        queue = PortPrinter.from_string(
            """
[print.air__density]
format=vtk
port=air_port
"""
        )
        assert isinstance(queue, PortPrinter)

        queue.open()
        queue.write()

        assert os.path.isfile("air__density_0000.vtu")


def test_multiple_printers(tmpdir, with_two_components):
    with tmpdir.as_cwd():
        queue = PortPrinter.from_string(
            """
[print.air__density]
format=vtk
port=air_port

[print.glacier_top_surface__slope]
format=nc
port=earth_port
"""
        )

        assert isinstance(queue, list)

        for printer in queue:
            printer.open()

        for _ in xrange(5):
            for printer in queue:
                printer.write()

        assert os.path.isfile("air__density_0000.vtu")
        assert os.path.isfile("air__density_0001.vtu")
        assert os.path.isfile("air__density_0002.vtu")
        assert os.path.isfile("air__density_0003.vtu")
        assert os.path.isfile("air__density_0004.vtu")
        assert os.path.isfile("glacier_top_surface__slope.nc")
