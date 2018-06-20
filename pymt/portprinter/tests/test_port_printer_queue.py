#! /usr/bin/env python
from six.moves import xrange

from nose.tools import assert_is_instance

from pymt.portprinter.port_printer import PortPrinter
from pymt.testing.assertions import assert_isfile_and_remove


def test_one_printer():
    queue = PortPrinter.from_string("""
[print.air__density]
format=vtk
port=air_port
""")
    assert_is_instance(queue, PortPrinter)

    queue.open()
    queue.write()

    assert_isfile_and_remove('air__density_0000.vtu')


def test_multiple_printers():
    queue = PortPrinter.from_string("""
[print.air__density]
format=vtk
port=air_port

[print.glacier_top_surface__slope]
format=nc
port=earth_port
""")

    assert_is_instance(queue, list)

    for printer in queue:
        printer.open()

    for _ in xrange(5):
        for printer in queue:
            printer.write()

    assert_isfile_and_remove('air__density_0000.vtu')
    assert_isfile_and_remove('air__density_0001.vtu')
    assert_isfile_and_remove('air__density_0002.vtu')
    assert_isfile_and_remove('air__density_0003.vtu')
    assert_isfile_and_remove('air__density_0004.vtu')
    assert_isfile_and_remove('glacier_top_surface__slope.nc')
