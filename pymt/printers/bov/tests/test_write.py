#! /usr/bin/env python
import os
import sys

import yaml
import numpy as np
from numpy.testing import assert_array_equal

from nose.tools import assert_true, assert_dict_equal, assert_raises

from pymt.grids import RasterField, RectilinearField
from pymt.printers.bov.bov_io import tofile, FileExists
from pymt.utils.run_dir import cd_temp


def test_1d():
    grid = RasterField((12,), (1.,), (0.,))
    point_data = np.arange(grid.get_point_count())
    grid.add_field("var_0", point_data, centering="point")

    with cd_temp() as _:
        tofile("test-1d", grid)

        assert_true(os.path.isfile("test-1d.bov"))
        assert_true(os.path.isfile("test-1d.dat"))

        data = np.fromfile("test-1d.dat", dtype=int)
        assert_array_equal(point_data, data)

        with open("test-1d.bov", "r") as fp:
            header = yaml.load(fp)

    assert_dict_equal(
        header,
        {
            "VARIABLE": "var_0",
            "BRICK_SIZE": "12.0 1.0 1.0",
            "DATA_FILE": "test-1d.dat",
            "DATA_SIZE": "12 1 1",
            "BRICK_ORIGIN": "0.0 1.0 1.0",
            "DATA_FORMAT": "INT",
            "DATA_ENDIAN": sys.byteorder.upper(),
        },
    )


def test_2d():
    grid = RasterField((3, 4), (1., 1.), (0., 0.))
    point_data = np.arange(grid.get_point_count())
    grid.add_field("var_0", point_data, centering="point")

    with cd_temp() as _:
        tofile("test-2d", grid)

        assert_true(os.path.isfile("test-2d.bov"))
        assert_true(os.path.isfile("test-2d.dat"))

        data = np.fromfile("test-2d.dat", dtype=int)
        assert_array_equal(point_data, data)

        with open("test-2d.bov", "r") as fp:
            header = yaml.load(fp)

    assert_dict_equal(
        header,
        {
            "VARIABLE": "var_0",
            "BRICK_SIZE": "3.0 4.0 1.0",
            "DATA_FILE": "test-2d.dat",
            "DATA_SIZE": "3 4 1",
            "BRICK_ORIGIN": "0.0 0.0 1.0",
            "DATA_FORMAT": "INT",
            "DATA_ENDIAN": sys.byteorder.upper(),
        },
    )


def test_3d():
    grid = RasterField((2, 3, 4), (1., 1., 1.), (0., 0., 0.))
    point_data = np.arange(grid.get_point_count())
    grid.add_field("var_0", point_data, centering="point")

    with cd_temp() as _:
        tofile("test-3d", grid)

        assert_true(os.path.isfile("test-3d.bov"))
        assert_true(os.path.isfile("test-3d.dat"))

        data = np.fromfile("test-3d.dat", dtype=int)
        assert_array_equal(point_data, data)

        with open("test-3d.bov", "r") as fp:
            header = yaml.load(fp)

    assert_dict_equal(
        header,
        {
            "VARIABLE": "var_0",
            "BRICK_SIZE": "2.0 3.0 4.0",
            "DATA_FILE": "test-3d.dat",
            "DATA_SIZE": "2 3 4",
            "BRICK_ORIGIN": "0.0 0.0 0.0",
            "DATA_FORMAT": "INT",
            "DATA_ENDIAN": sys.byteorder.upper(),
        },
    )


def test_all_fields():
    grid = RasterField((12,), (1.,), (0.,))
    var_0_data = np.arange(grid.get_point_count())
    var_1_data = np.arange(grid.get_point_count()) * 10
    grid.add_field("var_0", var_0_data, centering="point")
    grid.add_field("var_1", var_1_data, centering="point")

    with cd_temp() as _:
        tofile("test-1d", grid)

        assert_true(os.path.isfile("test-1d_var_0.bov"))
        assert_true(os.path.isfile("test-1d_var_0.dat"))
        assert_true(os.path.isfile("test-1d_var_1.bov"))
        assert_true(os.path.isfile("test-1d_var_1.dat"))

        data = np.fromfile("test-1d_var_0.dat", dtype=int)
        assert_array_equal(var_0_data, data)
        data = np.fromfile("test-1d_var_1.dat", dtype=int)
        assert_array_equal(var_1_data, data)


def test_clobber():
    grid = RasterField((12,), (1.,), (0.,))
    var_0_data = np.arange(grid.get_point_count())
    grid.add_field("var_0", var_0_data, centering="point")

    for fname in ["test-1d.bov", "test-1d.dat"]:
        with cd_temp() as _:
            with open(fname, "w") as fp:
                fp.write("empty_file")
            with assert_raises(FileExists):
                tofile("test-1d", grid, no_clobber=True)
            tofile("test-1d", grid)


def test_options():
    grid = RasterField((12,), (1.,), (0.,))
    var_0_data = np.arange(grid.get_point_count())
    grid.add_field("var_0", var_0_data, centering="point")

    with cd_temp() as _:
        tofile("test-1d", grid, options={"foo": "bar"})

        with open("test-1d.bov", "r") as fp:
            header = yaml.load(fp)

    assert_dict_equal(
        header,
        {
            "VARIABLE": "var_0",
            "BRICK_SIZE": "12.0 1.0 1.0",
            "DATA_FILE": "test-1d.dat",
            "DATA_SIZE": "12 1 1",
            "BRICK_ORIGIN": "0.0 1.0 1.0",
            "DATA_FORMAT": "INT",
            "DATA_ENDIAN": sys.byteorder.upper(),
            "foo": "bar",
        },
    )


def test_bad_grid():
    grid = RectilinearField((np.arange(12),))
    var_0_data = np.arange(grid.get_point_count())
    grid.add_field("var_0", var_0_data, centering="point")

    with cd_temp() as _:
        with assert_raises(TypeError):
            tofile("test-1d", grid)
