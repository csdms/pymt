from cmt.printqueue.port_printer import VtkPortPrinter
from cmt.testing.ports import UniformRectilinearGridPort
from cmt.testing.assertions import assert_isfile_and_remove


def test_one_file():
    port = UniformRectilinearGridPort()
    printer = VtkPortPrinter(port, 'landscape_surface__elevation')
    printer.open()
    printer.write()

    assert_isfile_and_remove('landscape_surface__elevation_0000.vtu')


def test_time_series():
    expected_files = [
        'sea_floor_surface_sediment__mean_of_grain_size_0000.vtu',
        'sea_floor_surface_sediment__mean_of_grain_size_0001.vtu',
        'sea_floor_surface_sediment__mean_of_grain_size_0002.vtu',
        'sea_floor_surface_sediment__mean_of_grain_size_0003.vtu',
        'sea_floor_surface_sediment__mean_of_grain_size_0004.vtu',
    ]

    port = UniformRectilinearGridPort()
    printer = VtkPortPrinter(
        port, 'sea_floor_surface_sediment__mean_of_grain_size')
    printer.open()
    for _ in xrange(5):
        printer.write()
    printer.close()

    for filename in expected_files:
        assert_isfile_and_remove(filename)


def test_multiple_files():
    port = UniformRectilinearGridPort()
    for _ in xrange(5):
        printer = VtkPortPrinter(port, 'sea_surface__temperature')
        printer.open()
        printer.write()
        printer.close()

    assert_isfile_and_remove('sea_surface__temperature_0000.vtu')
