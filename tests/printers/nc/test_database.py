import os

import numpy as np
import xarray as xr
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

        root = xr.open_dataset(nc_file, engine="h5netcdf")

        assert set(root.dims) == {"y", "x", "time"}
        assert set(root.data_vars) == {"mesh", "Elevation"}

        assert root.dims["x"] == 3
        assert root.dims["y"] == 2
        assert root.dims["time"] == 2

        assert root.variables["Elevation"].shape == (2, 2, 3)

        assert root.variables["Elevation"][0].data == approx(
            np.arange(6.0).reshape(2, 3)
        )
        assert root.variables["Elevation"][1].data == approx(
            np.arange(6.0).reshape((2, 3)) * 2.0
        )

        assert root.variables["y"].data == approx([0.0, 1.0])
        assert root.variables["x"].data == approx([0.0, 1.0, 2.0])

        assert root.data_vars["Elevation"].attrs["long_name"] == "Elevation"
        assert root.data_vars["Elevation"].attrs["units"] == "-"

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
        root = xr.open_dataset(nc_file, engine="h5netcdf")

        assert set(root.dims) == {"y", "x", "time"}
        assert set(root.data_vars) == {"mesh", "Temperature"}

        assert root.dims["x"] == 3
        assert root.dims["y"] == 3
        assert root.dims["time"] == 1

        assert root.data_vars["Temperature"].shape == (1, 3, 3)
        assert root.data_vars["Temperature"][0].data == approx(
            np.arange(9.0).reshape((3, 3))
        )

        assert root.variables["x"].data == approx([0.0, 1.0, 2.0])
        assert root.variables["y"].data == approx([0.0, 1.0, 2.0])

        assert root.data_vars["Temperature"].attrs["long_name"] == "Temperature"
        assert root.data_vars["Temperature"].attrs["units"] == "-"

        root.close()
