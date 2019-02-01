#! /usr/bin/env python
import os

import numpy as np
from pytest import approx

from pymt.grids import RasterField
from pymt.printers.nc.database import Database


def open_nc_file(filename):
    import netCDF4 as nc

    return nc.Dataset(filename, "r", format="NETCDF4")


def test_2d_constant_shape(tmpdir):
    # Create field and add some data to it that we will write to a
    # NetCDF file database.

    # nc_file = 'Elevation_time_series_0000.nc'
    nc_file = "2d_elevation_time_series.nc"

    data = np.arange(6.0)

    field = RasterField((2, 3), (1.0, 1.0), (0.0, 0.0), indexing="ij")
    field.add_field("Elevation", data, centering="point")

    # Create database of 'Elevation' values. Data are written to the
    # NetCDF file Elevation_time_series.nc.
    with tmpdir.as_cwd():
        db = Database()
        db.open(nc_file, "Elevation")
        db.write(field)

        assert os.path.isfile(nc_file)

        # Append data to the NetCDF file.
        data *= 2.0
        db.write(field)

        db.close()

        try:
            root = open_nc_file(nc_file)
        except Exception:
            raise AssertionError("%s: Could not open" % nc_file)
        else:
            assert list(root.dimensions.keys()) == ["y", "x", "time"]
            assert list(root.variables) == ["mesh", "y", "x", "Elevation", "time"]

            assert len(root.dimensions["x"]) == 3
            assert len(root.dimensions["y"]) == 2
            assert len(root.dimensions["time"]) == 2

            assert root.variables["Elevation"].shape == (2, 2, 3)

            assert root.variables["Elevation"][0].data == approx(
                np.arange(6.0).reshape(2, 3)
            )
            assert root.variables["Elevation"][1].data == approx(
                np.arange(6.0).reshape((2, 3)) * 2.0
            )

            assert root.variables["y"] == approx([0.0, 1.0])
            assert root.variables["x"] == approx([0.0, 1.0, 2.0])

            assert root.variables["Elevation"].long_name == "Elevation"
            assert root.variables["Elevation"].units == "-"

            root.close()


def test_2d_changing_shape(tmpdir):
    # Create field and add some data to it that we will write to a
    # NetCDF file database.

    nc_file = "Temperature_time_series.nc"

    data = np.arange(6.0)

    field = RasterField((3, 2), (1.0, 1.0), (0.0, 0.0))
    field.add_field("Temperature", data, centering="point")

    with tmpdir.as_cwd():
        db = Database()
        db.open(nc_file, "Temperature")
        db.write(field)

        assert os.path.isfile(nc_file)

        # Create a new field and write the data to the database. Since
        # the size of the field has changed, the data will be written
        # to a new file, Elevation_time_series_0000.nc.

        field = RasterField((3, 3), (1.0, 1.0), (0.0, 0.0))
        data = np.arange(9.0)
        field.add_field("Temperature", data, centering="point")

        db.write(field)
        assert os.path.isfile("Temperature_time_series_0000.nc")

        db.close()

        nc_file = "Temperature_time_series_0000.nc"
        try:
            root = open_nc_file(nc_file)
        except Exception:
            raise AssertionError("%s: Could not open" % nc_file)
        else:
            assert list(root.dimensions.keys()) == ["y", "x", "time"]
            assert list(root.variables) == ["mesh", "y", "x", "Temperature", "time"]

            assert len(root.dimensions["x"]) == 3
            assert len(root.dimensions["y"]) == 3
            assert len(root.dimensions["time"]) == 1

            assert root.variables["Temperature"].shape == (1, 3, 3)
            assert root.variables["Temperature"][0].data == approx(
                np.arange(9.0).reshape((3, 3))
            )

            assert root.variables["x"] == approx([0.0, 1.0, 2.0])
            assert root.variables["y"] == approx([0.0, 1.0, 2.0])

            assert root.variables["Temperature"].long_name == "Temperature"
            assert root.variables["Temperature"].units == "-"

            root.close()
