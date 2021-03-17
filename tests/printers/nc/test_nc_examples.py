#! /usr/bin/env python
import os

import numpy as np

from pymt.grids import RectilinearField
from pymt.printers.nc.write import field_tofile


def sample_surface(x, y, alpha, eta=1.0, purity=1.0):
    return (
        1.0
        + eta
        * (
            np.exp(-(x ** 2) - (y - alpha) ** 2)
            + np.exp(-(x ** 2) - (y + alpha) ** 2)
            + 2 * purity * np.exp(-(x ** 2) - y ** 2) * np.cos(2 * alpha * x)
        )
        / (2 * (1 + np.exp(-(alpha ** 2))))
    ) / 2.0


def sample_field():
    x = np.arange(100.0)
    y = np.arange(100.0)
    field = RectilinearField(y, x)
    field.add_field("probability", sample_surface(x, y, 1.0))
    return field


def rectilinear_1d_field():
    field = RectilinearField([0, 1, 2, 3, 4])
    data = np.arange(field.get_point_count())
    field.add_field("air__temperature", data, centering="point", units="F")
    return field


def rectilinear_2d_field():
    field = RectilinearField([-1, 0, 1], [2, 4, 6])
    data = np.arange(field.get_point_count())
    field.add_field("air__temperature", data, centering="point", units="F")
    return field


def rectilinear_3d_field():
    field = RectilinearField(
        [-1, 0, 1],
        [2, 4, 6],
        [10, 20, 30],
        coordinate_names=("elevation", "latitude", "longitude"),
        units=("m", "degrees_north", "degrees_east"),
    )
    data = np.arange(field.get_point_count(), dtype=float)
    field.add_field("air__temperature", data, centering="point", units="F")
    return field


def test_rectilinear_1d_netcdf(tmpdir):
    with tmpdir.as_cwd():
        field_tofile(rectilinear_1d_field(), "rectilinear.1d.nc")
        assert os.path.isfile("rectilinear.1d.nc")


def test_rectilinear_2d_netcdf(tmpdir):
    with tmpdir.as_cwd():
        field_tofile(rectilinear_2d_field(), "rectilinear.2d.nc")
        assert os.path.isfile("rectilinear.2d.nc")


def test_rectilinear_3d_netcdf(tmpdir):
    with tmpdir.as_cwd():
        field_tofile(rectilinear_3d_field(), "rectilinear.3d.nc")
        assert os.path.isfile("rectilinear.3d.nc")
