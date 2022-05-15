import os

from pymt.portprinter.port_printer import VtkPortPrinter
from pymt.testing.ports import UniformRectilinearGridPort


def test_one_file(tmpdir):
    port = UniformRectilinearGridPort()

    with tmpdir.as_cwd():
        printer = VtkPortPrinter(port, "landscape_surface__elevation")
        printer.open()
        printer.write()

        assert os.path.isfile("landscape_surface__elevation_0000.vtu")


def test_time_series(tmpdir):
    expected_files = [
        "sea_floor_surface_sediment__mean_of_grain_size_0000.vtu",
        "sea_floor_surface_sediment__mean_of_grain_size_0001.vtu",
        "sea_floor_surface_sediment__mean_of_grain_size_0002.vtu",
        "sea_floor_surface_sediment__mean_of_grain_size_0003.vtu",
        "sea_floor_surface_sediment__mean_of_grain_size_0004.vtu",
    ]

    port = UniformRectilinearGridPort()

    with tmpdir.as_cwd():
        printer = VtkPortPrinter(port, "sea_floor_surface_sediment__mean_of_grain_size")
        printer.open()
        for _ in range(5):
            printer.write()
        printer.close()

        for filename in expected_files:
            assert os.path.isfile(filename)


def test_multiple_files(tmpdir):
    port = UniformRectilinearGridPort()

    with tmpdir.as_cwd():
        for _ in range(5):
            printer = VtkPortPrinter(port, "sea_surface__temperature")
            printer.open()
            printer.write()
            printer.close()

        assert os.path.isfile("sea_surface__temperature_0000.vtu")


def test_port_as_string(tmpdir, with_two_components):
    with tmpdir.as_cwd():
        printer = VtkPortPrinter("air_port", "air__density")
        printer.open()
        printer.write()
        printer.close()

        assert os.path.isfile("air__density_0000.vtu")
