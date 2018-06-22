#! /usr/bin/env python

import os
import unittest
import numpy as np

from pymt.grids import RasterField, RectilinearField, StructuredField, UnstructuredField
from pymt.printers.vtk.vtu import tofile as field_tofile


class TestVtk(unittest.TestCase):
    vtk_files = dict()

    def setUp(self):
        for filename in self.vtk_files.values():
            try:
                os.remove(filename)
            except OSError:
                pass

    def tearDown(self):
        for filename in self.vtk_files.values():
            try:
                os.remove(filename)
            except OSError:
                pass


class TestUniformRectilinearVtk(TestVtk):
    vtk_files = dict(
        test_0d="test-0d-00.vtk",
        test_1d="test-1d-00.vtk",
        test_2d="test-2d-00.vtk",
        test_3d="test-3d-00.vtk",
    )

    @unittest.skip("0-D fields not supported")
    def test_0d(self):
        vtk_file = self.vtk_files["test_0d"]
        field = RasterField((1,), (0,), (0,), indexing="ij", units=("m",))

        attrs = dict(description="Example 0D nc file", author="Eric")
        for i in range(10):
            field.add_field("Elevation", i * 10., centering="point")
            field_tofile(field, vtk_file, attrs=attrs, append=True)

        self.assertTrue(os.path.isfile(vtk_file))

    def test_2d(self):
        vtk_file = self.vtk_files["test_2d"]
        field = RasterField((3, 2), (2., 1), (0, 0.5), indexing="ij", units=("m", "km"))

        data = np.arange(6.)

        field.add_field("Temperature", data * 10, centering="point", units="C")
        field.add_field("Elevation", data, centering="point", units="meters")
        field.add_field("Velocity", data * 100, centering="point", units="m/s")
        field.add_field("Temp", data * 2, centering="point", units="F")

        attrs = dict(description="Example nc file", author="Eric")
        field_tofile(field, vtk_file, attrs=attrs, append=True)

        self.assertTrue(os.path.isfile(vtk_file))

    def test_3d(self):
        vtk_file = self.vtk_files["test_3d"]

        field = RasterField(
            (2, 3, 4), (1, 2, 3), (-1, 0, 1), indexing="ij", units=("mm", "m", "km")
        )

        data = np.arange(24.)
        field.add_field("Temperature", data * 10, centering="point", units="C")
        field.add_field("Elevation", data, centering="point", units="meters")
        field.add_field("Velocity", data * 100, centering="point", units="m/s")
        field.add_field("Temp", data * 2, centering="point", units="F")

        attrs = dict(description="Example 3D nc file", author="Eric")
        field_tofile(field, vtk_file, attrs=attrs, append=True)

        self.assertTrue(os.path.isfile(vtk_file))

    def test_1d(self):
        vtk_file = self.vtk_files["test_1d"]
        field = RasterField((12,), (1,), (-1,), indexing="ij", units=("m",))
        data = np.arange(12.)
        field.add_field("Elevation", data, centering="point")

        attrs = dict(description="Example 1D nc file", author="Eric")
        field_tofile(field, vtk_file, attrs=attrs, append=True)

        self.assertTrue(os.path.isfile(vtk_file))


class TestRectilinearVtk(TestVtk):
    vtk_files = dict(
        test_0d="test-0d-00-rectilinear.vtk",
        test_1d="test-1d-00-rectilinear.vtk",
        test_2d="test-2d-00-rectilinear.vtk",
        test_3d="test-3d-00-rectilinear.vtk",
    )

    def test_1d(self):
        vtk_file = self.vtk_files["test_1d"]

        field = RectilinearField((1, 2, 4, 5), indexing="ij", units=("m",))
        data = np.arange(4.)
        field.add_field("Elevation", data, centering="point")

        attrs = dict(description="Example 1D nc file", author="Eric")
        field_tofile(field, vtk_file, attrs=attrs, append=True)

        self.assertTrue(os.path.isfile(vtk_file))

    def test_2d(self):
        vtk_file = self.vtk_files["test_2d"]

        field = RectilinearField(
            (1, 4, 5),
            (2, 3),
            indexing="ij",
            units=("degrees_north", "degrees_east"),
            coordinate_names=["latitude", "longitude"],
        )

        data = np.arange(6.)

        field.add_field("Temperature", data * 10, centering="point", units="C")
        field.add_field("Elevation", data, centering="point", units="meters")
        field.add_field("Velocity", data * 100, centering="point", units="m/s")
        field.add_field("Temp", data * 2, centering="point", units="F")

        attrs = dict(description="Example nc file", author="Eric")
        field_tofile(field, vtk_file, attrs=attrs, append=True)

        self.assertTrue(os.path.isfile(vtk_file))


class TestStructuredVtk(TestVtk):
    vtk_files = dict(
        test_0d="test-0d-00-structured.vtk",
        test_1d="test-1d-00-structured.vtk",
        test_2d="test-2d-00-structured.vtk",
        test_3d="test-3d-00-structured.vtk",
    )

    def test_1d(self):
        vtk_file = self.vtk_files["test_1d"]

        field = StructuredField((1, 2, 4, 5), (4,), indexing="ij", units=("m",))
        data = np.arange(4.)
        field.add_field("Elevation", data, centering="point")

        attrs = dict(description="Example 1D nc file", author="Eric")
        field_tofile(field, vtk_file, attrs=attrs, append=True)

        self.assertTrue(os.path.isfile(vtk_file))

    def test_2d(self):
        vtk_file = self.vtk_files["test_2d"]

        field = StructuredField(
            (1, 4, 5, 1, 4, 5),
            (2, 3, 2, 3, 2, 3),
            (3, 2),
            indexing="ij",
            units=("m", "km"),
        )

        data = np.arange(6.)

        field.add_field("Temperature", data * 10, centering="point", units="C")
        field.add_field("Elevation", data, centering="point", units="meters")
        field.add_field("Velocity", data * 100, centering="point", units="m/s")
        field.add_field("Temp", data * 2, centering="point", units="F")

        attrs = dict(description="Example nc file", author="Eric")
        field_tofile(field, vtk_file, attrs=attrs, append=True)

        self.assertTrue(os.path.isfile(vtk_file))


class TestUnstructuredVtk(TestVtk):
    vtk_files = dict(
        test_0d="test-0d-00.vtu",
        test_1d="test-1d-00.vtu",
        test_2d="test-2d-00.vtu",
        test_3d="test-3d-00.vtu",
    )

    def test_1d(self):
        vtk_file = self.vtk_files["test_1d"]

        field = UnstructuredField(
            [0, 1, 4, 10], [0, 1, 1, 2, 2, 3], [2, 4, 6], units=("m",)
        )

        field.add_field("point_field", np.arange(4), centering="point", units="C")
        field.add_field("cell_field", np.arange(3) * 10., centering="zonal", units="F")

        field_tofile(field, vtk_file, append=False)

    def test_2d(self):
        vtk_file = self.vtk_files["test_2d"]

        field = UnstructuredField(
            [0, 2, 1, 3], [0, 0, 1, 1], [0, 2, 1, 2, 3, 1], [3, 6], units=("m", "m")
        )

        data = np.arange(4)
        field.add_field("point_field", data, centering="point", units="m")

        data = np.arange(2)
        field.add_field("cell_field", data, centering="zonal", units="m^2")

        field_tofile(field, vtk_file, append=False)
