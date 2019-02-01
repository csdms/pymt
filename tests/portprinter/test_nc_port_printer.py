import os

from six.moves import xrange

from pymt.portprinter.port_printer import NcPortPrinter
from pymt.testing.ports import UniformRectilinearGridPort


def test_default(tmpdir):
    port = UniformRectilinearGridPort()
    with tmpdir.as_cwd():
        printer = NcPortPrinter(port, "landscape_surface__elevation")
        printer.open()
        printer.write()

        assert os.path.isfile(filename)


def test_multiple_files(tmpdir):
    expected_files = [
        "sea_surface__temperature.nc",
        "sea_surface__temperature.0.nc",
        "sea_surface__temperature.1.nc",
        "sea_surface__temperature.2.nc",
        "sea_surface__temperature.3.nc",
    ]

    port = UniformRectilinearGridPort()
    with tmpdir.as_cwd():
        for _ in xrange(5):
            printer = NcPortPrinter(port, "sea_surface__temperature")
            printer.open()
            printer.write()

        for filename in expected_files:
            assert os.path.isfile(filename)


def test_time_series(tmpdir):
    port = UniformRectilinearGridPort()
    with tmpdir.as_cwd():
        printer = NcPortPrinter(port, "sea_floor_surface_sediment__mean_of_grain_size")
        printer.open()
        for _ in xrange(5):
            printer.write()
        printer.close()

        assert os.path.isfile("sea_floor_surface_sediment__mean_of_grain_size.nc")
