#! /usr/bin/env python
import os
import sys

import numpy as np
import pytest
import yaml

from pymt.grids import RasterField, RectilinearField
from pymt.printers.bov.bov_io import FileExists, tofile


def test_1d(tmpdir):
    grid = RasterField((12,), (1.,), (0.,))
    point_data = np.arange(grid.get_point_count())
    grid.add_field("var_0", point_data, centering="point")

    with tmpdir.as_cwd():
        tofile("test-1d", grid)

        assert os.path.isfile("test-1d.bov")
        assert os.path.isfile("test-1d.dat")

        data = np.fromfile("test-1d.dat", dtype=int)
        assert np.all(point_data == data)

        with open("test-1d.bov", "r") as fp:
            header = yaml.load(fp)

    assert header == {
        "VARIABLE": "var_0",
        "BRICK_SIZE": "12.0 1.0 1.0",
        "DATA_FILE": "test-1d.dat",
        "DATA_SIZE": "12 1 1",
        "BRICK_ORIGIN": "0.0 1.0 1.0",
        "DATA_FORMAT": "INT",
        "DATA_ENDIAN": sys.byteorder.upper(),
    }


def test_2d(tmpdir):
    grid = RasterField((3, 4), (1., 1.), (0., 0.))
    point_data = np.arange(grid.get_point_count())
    grid.add_field("var_0", point_data, centering="point")

    with tmpdir.as_cwd():
        tofile("test-2d", grid)

        assert os.path.isfile("test-2d.bov")
        assert os.path.isfile("test-2d.dat")

        data = np.fromfile("test-2d.dat", dtype=int)
        assert np.all(point_data == data)

        with open("test-2d.bov", "r") as fp:
            header = yaml.load(fp)

    assert header == {
        "VARIABLE": "var_0",
        "BRICK_SIZE": "3.0 4.0 1.0",
        "DATA_FILE": "test-2d.dat",
        "DATA_SIZE": "3 4 1",
        "BRICK_ORIGIN": "0.0 0.0 1.0",
        "DATA_FORMAT": "INT",
        "DATA_ENDIAN": sys.byteorder.upper(),
    }


def test_3d(tmpdir):
    grid = RasterField((2, 3, 4), (1., 1., 1.), (0., 0., 0.))
    point_data = np.arange(grid.get_point_count())
    grid.add_field("var_0", point_data, centering="point")

    with tmpdir.as_cwd():
        tofile("test-3d", grid)

        assert os.path.isfile("test-3d.bov")
        assert os.path.isfile("test-3d.dat")

        data = np.fromfile("test-3d.dat", dtype=int)
        assert np.all(point_data == data)

        with open("test-3d.bov", "r") as fp:
            header = yaml.load(fp)

    assert header == {
        "VARIABLE": "var_0",
        "BRICK_SIZE": "2.0 3.0 4.0",
        "DATA_FILE": "test-3d.dat",
        "DATA_SIZE": "2 3 4",
        "BRICK_ORIGIN": "0.0 0.0 0.0",
        "DATA_FORMAT": "INT",
        "DATA_ENDIAN": sys.byteorder.upper(),
    }


def test_all_fields(tmpdir):
    grid = RasterField((12,), (1.,), (0.,))
    var_0_data = np.arange(grid.get_point_count())
    var_1_data = np.arange(grid.get_point_count()) * 10
    grid.add_field("var_0", var_0_data, centering="point")
    grid.add_field("var_1", var_1_data, centering="point")

    with tmpdir.as_cwd():
        tofile("test-1d", grid)

        assert os.path.isfile("test-1d_var_0.bov")
        assert os.path.isfile("test-1d_var_0.dat")
        assert os.path.isfile("test-1d_var_1.bov")
        assert os.path.isfile("test-1d_var_1.dat")

        data = np.fromfile("test-1d_var_0.dat", dtype=int)
        assert np.all(var_0_data == data)
        data = np.fromfile("test-1d_var_1.dat", dtype=int)
        assert np.all(var_1_data == data)


def test_clobber(tmpdir):
    grid = RasterField((12,), (1.,), (0.,))
    var_0_data = np.arange(grid.get_point_count())
    grid.add_field("var_0", var_0_data, centering="point")

    for fname in ["test-1d.bov", "test-1d.dat"]:
        with tmpdir.as_cwd():
            with open(fname, "w") as fp:
                fp.write("empty_file")
            with pytest.raises(FileExists):
                tofile("test-1d", grid, no_clobber=True)
            tofile("test-1d", grid)


def test_options(tmpdir):
    grid = RasterField((12,), (1.,), (0.,))
    var_0_data = np.arange(grid.get_point_count())
    grid.add_field("var_0", var_0_data, centering="point")

    with tmpdir.as_cwd():
        tofile("test-1d", grid, options={"foo": "bar"})

        with open("test-1d.bov", "r") as fp:
            header = yaml.load(fp)

    assert header == {
        "VARIABLE": "var_0",
        "BRICK_SIZE": "12.0 1.0 1.0",
        "DATA_FILE": "test-1d.dat",
        "DATA_SIZE": "12 1 1",
        "BRICK_ORIGIN": "0.0 1.0 1.0",
        "DATA_FORMAT": "INT",
        "DATA_ENDIAN": sys.byteorder.upper(),
        "foo": "bar",
    }


def test_bad_grid(tmpdir):
    grid = RectilinearField((np.arange(12),))
    var_0_data = np.arange(grid.get_point_count())
    grid.add_field("var_0", var_0_data, centering="point")

    with tmpdir.as_cwd():
        with pytest.raises(TypeError):
            tofile("test-1d", grid)
