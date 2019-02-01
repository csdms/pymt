from __future__ import print_function

import unittest

import numpy as np

from pymt.printers.nc.ugrid import (
    NetcdfRectilinearField,
    NetcdfStructuredField,
    NetcdfUnstructuredField,
)


class UniqueNameMixIn(object):
    def unique_name(self, **kwds):
        import tempfile
        import os

        if "dir" not in kwds:
            kwds["dir"] = os.getcwd()

        (handle, name) = tempfile.mkstemp(**kwds)
        os.close(handle)
        try:
            self._temp_files.append(name)
        except AttributeError:
            self._temp_files = [name]
        return name

    def open_unique(self, **kwds):
        import netCDF4 as nc4
        import tempfile

        (handle, name) = tempfile.mkstemp(**kwds)
        handle.close()

        root = nc4.Dataset(name, "w", format="NETCDF4")
        try:
            self._temp_files.append(name)
        except AttributeError:
            self._temp_files = [name]
        return root

    def tearDown(self):
        import os

        for file in self._temp_files:
            try:
                os.remove(file)
            except OSError as error:
                print(error)
                pass


class FieldMixIn(object):
    def new_raster(self, **kwds):
        from pymt.grids import RasterField

        ndims = kwds.pop("ndims", 1)
        shape = np.random.randint(3, 101 + 1, ndims)
        spacing = (1.0 - np.random.random(ndims)) * 100.0
        origin = (np.random.random(ndims) - 0.5) * 100.0

        return RasterField(shape, spacing, origin, **kwds)

    def new_rectilinear(self, **kwds):
        from pymt.grids import RectilinearField

        ndims = kwds.pop("ndims", 1)
        shape = np.random.randint(2, 101 + 1, ndims)
        args = []
        for size in shape:
            args.append(np.cumsum((1.0 - np.random.random(size))))

        return RectilinearField(*args, **kwds)

    def new_structured(self, **kwds):
        from pymt.grids import StructuredField

        ndims = kwds.pop("ndims", 1)
        shape = np.random.randint(2, 101 + 1, ndims)
        np.prod(shape)

        coords = []
        for size in shape:
            coords.append(np.cumsum((1.0 - np.random.random(size))))

        if len(coords) > 1:
            args = np.meshgrid(*coords, indexing="ij")
        else:
            args = coords
        args.append(shape)

        return StructuredField(*args, **kwds)


class TestRectilinearUgrid(UniqueNameMixIn, unittest.TestCase, FieldMixIn):
    def test_1d_points(self):
        field = self.new_rectilinear()
        data = np.arange(field.get_point_count())
        field.add_field("air_temperature", data, centering="point", units="F")

        NetcdfRectilinearField(
            self.unique_name(prefix="rectilinear.1d.", suffix=".nc"), field
        )

    def test_2d_points(self):
        field = self.new_rectilinear(ndims=2)
        data = np.arange(field.get_point_count(), dtype=float)
        field.add_field("air__temperature", data, centering="point", units="F")

        NetcdfRectilinearField(
            self.unique_name(prefix="rectilinear.2d.", suffix=".nc"), field
        )

    def test_3d_points(self):
        field = self.new_rectilinear(
            ndims=3,
            coordinate_names=("elevation", "latitude", "longitude"),
            units=("m", "degrees_north", "degrees_east"),
        )
        data = np.arange(field.get_point_count(), dtype=float)
        field.add_field("air__temperature", data, centering="point", units="F")

        NetcdfRectilinearField(
            self.unique_name(prefix="rectilinear.3d.", suffix=".nc"), field
        )


class TestStructuredUgrid(UniqueNameMixIn, unittest.TestCase, FieldMixIn):
    def test_1d_points(self):
        field = self.new_rectilinear()
        data = np.arange(field.get_point_count())
        field.add_field("air_temperature", data, centering="point", units="F")

        NetcdfStructuredField(
            self.unique_name(prefix="structured.1d.", suffix=".nc"), field
        )

    def test_2d_points(self):
        field = self.new_rectilinear(ndims=2)
        data = np.arange(field.get_point_count(), dtype=float)
        field.add_field("air__temperature", data, centering="point", units="F")

        NetcdfStructuredField(
            self.unique_name(prefix="structured.2d.", suffix=".nc"), field
        )

    def test_3d_points(self):
        field = self.new_rectilinear(
            ndims=3,
            coordinate_names=("elevation", "latitude", "longitude"),
            units=("m", "degrees_north", "degrees_east"),
        )
        data = np.arange(field.get_point_count(), dtype=float)
        field.add_field("air__temperature", data, centering="point", units="F")

        NetcdfStructuredField(
            self.unique_name(prefix="structured.3d.", suffix=".nc"), field
        )


class TestUnstructuredUgrid(UniqueNameMixIn, unittest.TestCase, FieldMixIn):
    def test_1d_points(self):
        field = self.new_rectilinear()
        data = np.arange(field.get_point_count())
        field.add_field("air_temperature", data, centering="point", units="F")

        NetcdfUnstructuredField(
            self.unique_name(prefix="unstructured.1d.", suffix=".nc"), field
        )

    def test_2d_points(self):
        field = self.new_rectilinear(ndims=2)
        data = np.arange(field.get_point_count(), dtype=float)
        field.add_field("air__temperature", data, centering="point", units="F")

        NetcdfUnstructuredField(
            self.unique_name(prefix="unstructured.2d.", suffix=".nc"), field
        )

    def test_3d_points(self):
        field = self.new_rectilinear(
            ndims=3,
            coordinate_names=("elevation", "latitude", "longitude"),
            units=("m", "degrees_north", "degrees_east"),
        )
        data = np.arange(field.get_point_count(), dtype=float)
        field.add_field("air__temperature", data, centering="point", units="F")

        NetcdfUnstructuredField(
            self.unique_name(prefix="unstructured.3d.", suffix=".nc"), field
        )
