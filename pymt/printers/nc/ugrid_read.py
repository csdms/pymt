#! /usr/bin/env python
from six.moves import xrange

from ...grids import RectilinearField, StructuredField, UnstructuredField
from ...grids import utils as gutils
from .constants import open_netcdf


class NetcdfFieldReader(object):
    def __init__(self, path, fmt="NETCDF4"):
        self._path = path

        self._root = open_netcdf(path, mode="r", fmt=fmt)
        self._topology = self._get_mesh_topology()
        self._field = None
        self._time = []

        self._get_mesh_coordinate_data()
        self._get_node_variable_data()
        self._get_face_variable_data()
        if self.contains_time_dimension():
            self._get_time_variable()

        self._root.close()

    @property
    def fields(self):
        return self._field

    @property
    def times(self):
        return self._time

    def _get_mesh_coordinate_data(self):
        raise NotImplementedError("_get_mesh_coordinate_data")

    def contains_time_dimension(self):
        return "time" in self._root.dimensions

    def is_variable_data(self, name):
        var = self._root.variables[name]
        return (
            hasattr(var, "standard_name")
            and hasattr(var, "units")
            and hasattr(var, "coordinates")
            and hasattr(var, "location")
        )

    def variable_data_names(self):
        names = []
        for name in self._root.variables:
            if self.is_variable_data(name):
                names.append(name)
        return names

    def variable_data(self, name):
        return self._root.variables[name][:]

    def _get_mesh_topology(self):
        topology = self._root.variables["mesh"]
        try:
            assert topology.type in ["rectilinear", "structured", "unstructured"]
        except AttributeError:
            pass

        return topology

    def _get_node_variable_data(self):
        for name in self.variable_data_names():
            if self._root.variables[name].location == "node":
                data = self.variable_data(name)
                if self.contains_time_dimension():
                    for time in xrange(len(self.time)):
                        self._field.add_field(
                            name + "@t=%d" % time, data[time, :], centering="point"
                        )
                    self._field.add_field(name, data[-1, :], centering="point")
                else:
                    self._field.add_field(name, data[:], centering="point")

    def _get_face_variable_data(self):
        for name in self.variable_data_names():
            if self._root.variables[name].location == "face":
                data = self.variable_data(name)
                if self.contains_time_dimension():
                    for time in xrange(len(self.time)):
                        self._field.add_field(
                            name + "@t=%d" % time, data[time, :], centering="cell"
                        )
                    self._field.add_field(name, data[-1, :], centering="cell")
                else:
                    self._field.add_field(name, data[:], centering="cell")

    def _get_time_variable(self):
        if self.contains_time_dimension():
            self._time = self.variable_data("time")
        else:
            self._time = []

    @property
    def time(self):
        if self.contains_time_dimension():
            return self.variable_data("time")
        else:
            return []


class NetcdfRectilinearFieldReader(NetcdfFieldReader):
    def _get_mesh_coordinate_data(self):
        coordinate_names = self._topology.node_coordinates.split()
        coordinates = []
        for name in coordinate_names:
            coordinates.append(self._root.variables[name][:])
        self._field = RectilinearField(*coordinates)


class NetcdfStructuredFieldReader(NetcdfFieldReader):
    def _get_mesh_coordinate_data(self):
        coordinate_names = self._topology.node_coordinates.split()
        coordinates, shape = ([], [])
        for name in coordinate_names:
            coordinates.append(self._root.variables[name])
            shape.append(len(self._root.dimensions[name]))
        self._field = StructuredField(*(coordinates + [shape]))


class NetcdfUnstructuredFieldReader(NetcdfFieldReader):
    def face_nodes_data(self):
        name = self._topology.face_node_connectivity
        return self._root.variables[name]

    def face_nodes_fill_value(self):
        name = self._topology.face_node_connectivity
        return self._root.variables[name]._FillValue

    def face_nodes_start_index(self):
        name = self._topology.face_node_connectivity
        return self._root.variables[name].start_index

    def _get_mesh_coordinate_data(self):
        coordinate_names = self._topology.node_coordinates.split()
        coordinates = []
        for name in coordinate_names:
            coordinates.append(self._root.variables[name])

        (connectivity, offset) = gutils.connectivity_matrix_as_array(
            self.face_nodes_data(), self.face_nodes_fill_value
        )
        connectivity -= self.face_nodes_start_index()
        self._field = UnstructuredField(
            *coordinates, connectivity=connectivity, offset=offset
        )
