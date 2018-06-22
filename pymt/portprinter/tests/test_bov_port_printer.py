from six.moves import xrange

from pymt.portprinter.port_printer import BovPortPrinter, PortPrinter
from pymt.testing.ports import UniformRectilinearGridPort
from pymt.testing.assertions import assert_isfile_and_remove


def test_default():
    port = UniformRectilinearGridPort()
    printer = BovPortPrinter(port, "landscape_surface__elevation")
    printer.open()
    printer.write()

    assert_isfile_and_remove("landscape_surface__elevation_0000.dat")
    assert_isfile_and_remove("landscape_surface__elevation_0000.bov")


def test_multiple_files():
    port = UniformRectilinearGridPort()
    for _ in xrange(5):
        printer = BovPortPrinter(port, "sea_surface__temperature")
        printer.open()
        printer.write()

    assert_isfile_and_remove("sea_surface__temperature_0000.dat")
    assert_isfile_and_remove("sea_surface__temperature_0000.bov")


def test_time_series():
    expected_files = [
        "sea_floor_surface_sediment__mean_of_grain_size_0000.dat",
        "sea_floor_surface_sediment__mean_of_grain_size_0000.bov",
        "sea_floor_surface_sediment__mean_of_grain_size_0001.dat",
        "sea_floor_surface_sediment__mean_of_grain_size_0001.bov",
        "sea_floor_surface_sediment__mean_of_grain_size_0002.dat",
        "sea_floor_surface_sediment__mean_of_grain_size_0002.bov",
        "sea_floor_surface_sediment__mean_of_grain_size_0003.dat",
        "sea_floor_surface_sediment__mean_of_grain_size_0003.bov",
        "sea_floor_surface_sediment__mean_of_grain_size_0004.dat",
        "sea_floor_surface_sediment__mean_of_grain_size_0004.bov",
    ]

    port = UniformRectilinearGridPort()
    printer = BovPortPrinter(port, "sea_floor_surface_sediment__mean_of_grain_size")
    printer.open()
    for _ in xrange(5):
        printer.write()
    printer.close()

    for filename in expected_files:
        assert_isfile_and_remove(filename)


def test_from_string():
    ini_string = """
[print.air__temperature]
format=bov
port=air_port
    """
    printer = PortPrinter.from_string(ini_string, "print.air__temperature")
