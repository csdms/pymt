from cmt.printqueue.port_printer import NcPortPrinter
from cmt.testing.ports import UniformRectilinearGridPort
from cmt.testing.assertions import assert_isfile_and_remove


def test_default():
    port = UniformRectilinearGridPort()
    printer = NcPortPrinter(port, 'landscape_surface__elevation')
    printer.open()
    printer.write()

    assert_isfile_and_remove('landscape_surface__elevation.nc')


def test_multiple_files():
    expected_files = [
        'sea_surface__temperature.nc',
        'sea_surface__temperature.0.nc',
        'sea_surface__temperature.1.nc',
        'sea_surface__temperature.2.nc',
        'sea_surface__temperature.3.nc',
    ]

    port = UniformRectilinearGridPort()
    for _ in xrange(5):
        printer = NcPortPrinter(port, 'sea_surface__temperature')
        printer.open()
        printer.write()

    for filename in expected_files:
        assert_isfile_and_remove(filename)


def test_time_series():
    port = UniformRectilinearGridPort()
    printer = NcPortPrinter(port,
                            'sea_floor_surface_sediment__mean_of_grain_size')
    printer.open()
    for _ in xrange(5):
        printer.write()
    printer.close()

    assert_isfile_and_remove(
        'sea_floor_surface_sediment__mean_of_grain_size.nc')
