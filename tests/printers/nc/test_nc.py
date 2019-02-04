#! /usr/bin/env python
import os

import numpy as np
import pytest
import xarray

from pymt.grids import RasterField, RectilinearField, StructuredField, UnstructuredField
from pymt.printers.nc.write import field_tofile


@pytest.mark.parametrize("ndims", (0, 1, 2, 3))
def test_raster(tmpdir, ndims):
    if ndims == 0:
        shape = (1,)
        ndims = 1
    else:
        shape = np.random.randint(1, 101, ndims)

    spacing = np.ones(ndims, dtype=float)
    origin = np.zeros(ndims, dtype=float)
    units = ["m"] * ndims

    field = RasterField(shape, spacing, origin, units=units)

    attrs = {
        "description": "Example {ndims}D nc file".format(ndims=ndims, author="pytest"),
    }
    data = np.arange(field.get_point_count())

    with tmpdir.as_cwd():
        for i in range(10):
            field.add_field("Elevation", data * i, centering="point", units="m")
            field_tofile(field, "raster.nc", attrs=attrs, append=True)

        assert os.path.isfile("raster.nc")

        ds = xarray.open_dataset("raster.nc")

        assert {"mesh", "Elevation", "time"}.issubset(ds.variables)
        assert "time" in ds.dims

        assert ds["Elevation"].long_name == "Elevation"
        assert ds["Elevation"].units == "m"


@pytest.mark.parametrize("ndims", (1, 2))
def test_rectilinear(tmpdir, ndims):
    coords = [np.arange(dim) for dim in np.random.randint(1, 101, ndims)]
    field = RectilinearField(*coords, units=["m"] * ndims)

    data = np.arange(field.get_point_count())
    field.add_field("Elevation", data, centering="point")

    attrs = dict(description="Example {0}D nc file".format(ndims), author="pytest")

    with tmpdir.as_cwd():
        field_tofile(field, "rectilinear.nc", attrs=attrs, append=True)

        assert os.path.isfile("rectilinear.nc")


@pytest.mark.parametrize("ndims", (1, 2))
def test_structured(tmpdir, ndims):
    shape = np.random.randint(1, 101, ndims)
    coords = [np.arange(dim) for dim in shape]

    field = StructuredField(
        *np.meshgrid(*coords),
        shape,
        indexing="ij",
        units=["m"] * ndims,
    )

    data = np.arange(field.get_point_count())

    field.add_field("Temperature", data * 10, centering="point", units="C")
    field.add_field("Elevation", data, centering="point", units="meters")
    field.add_field("Velocity", data * 100, centering="point", units="m/s")
    field.add_field("Temp", data * 2, centering="point", units="F")

    attrs = dict(description="Example nc file", author="pytest")
    with tmpdir.as_cwd():
        field_tofile(field, "structured.nc", attrs=attrs, append=True)

        assert os.path.isfile("structured.nc")


def test_unstructured_1(tmpdir):
    field = UnstructuredField(
        [0, 1, 4, 10], [0, 1, 1, 2, 2, 3], [2, 4, 6], units=("m",)
    )

    field.add_field("point_field", np.arange(4), centering="point", units="C")
    field.add_field("cell_field", np.arange(3) * 10.0, centering="zonal", units="F")

    with tmpdir.as_cwd():
        field_tofile(field, "unstructured.nc", append=False)
        assert os.path.isfile("unstructured.nc")


def test_unstructured_2(tmpdir):
    field = UnstructuredField(
        [0, 0, 1, 1], [0, 2, 1, 3], [0, 2, 1, 2, 3, 1], [3, 6], units=("m", "m")
    )

    data = np.arange(4)
    field.add_field("point_field", data, centering="point", units="m")

    data = np.arange(2)
    field.add_field("cell_field", data, centering="zonal", units="m^2")

    with tmpdir.as_cwd():
        field_tofile(field, "unstructured.nc", append=False)
        assert os.path.isfile("unstructured.nc")
