import os

from ...grids import utils as gutils
from .constants import _NP_TO_NC_TYPE, open_netcdf

_OPENED_FILES = {}


def close_all():
    for path in _OPENED_FILES:
        close(path)


def close(path):
    try:
        _OPENED_FILES[path].close()
    except KeyError:
        pass
    else:
        del _OPENED_FILES[path]


class NetcdfField:
    def __init__(
        self, path, field, fmt="NETCDF4", append=False, time=None, keep_open=False
    ):
        path = os.path.abspath(path)
        self._path = path
        self._field = field

        if path in _OPENED_FILES and not os.path.isfile(path):
            close(path)

        if path in _OPENED_FILES:
            self._root = _OPENED_FILES[path]
        else:
            self._root = open_netcdf(path, mode="w", fmt=fmt, append=append)

        self._set_mesh_topology()
        self._set_node_variable_data()
        self._set_face_variable_data()
        self._set_time_variable(now=time)

        if keep_open:
            _OPENED_FILES[path] = self._root
        else:
            self.close()

    def _set_mesh_dimensions(self):
        raise NotImplementedError("_set_mesh_dimensions")

    def _set_mesh_coordinate_data(self):
        raise NotImplementedError("_set_mesh_coordinate_data")

    @property
    def node_data_dimensions(self):
        raise NotImplementedError("node_data_dimensions")

    @property
    def face_data_dimensions(self):
        raise NotImplementedError("face_data_dimensions")

    def close(self):
        if self._path in _OPENED_FILES:
            del _OPENED_FILES[self._path]
        self._root.close()

    @property
    def type(self):
        return "unknown"

    @property
    def field(self):
        return self._field

    @property
    def root(self):
        return self._root

    @property
    def topology_dimension(self):
        return len(gutils.non_singleton_shape(self.field))

    @property
    def field_axes(self):
        return gutils.non_singleton_axes(self.field)

    @property
    def node_coordinates(self):
        return ""

    @property
    def face_connectivity(self):
        return "face_nodes_connectivity"

    @property
    def face_node_connectivity(self):
        return "face_nodes"

    @property
    def node_count(self):
        return self.field.get_point_count()

    @property
    def face_count(self):
        return self.field.get_cell_count()

    @property
    def vertex_count(self):
        return self.field.get_vertex_count()

    @property
    def time_count(self):
        try:
            return len(self._root.variables["time"])
        except KeyError:
            return 0

    def has_dimension(self, name):
        return name in self._root.dimensions

    def has_variable(self, name):
        return name in self._root.variables

    def create_dimension(self, name, dim_len):
        try:
            if not self.has_dimension(name):
                self._root.createDimension(name, dim_len)
        except IndexError:
            pass

    def create_variable(self, name, *args, **kwds):
        if not self.has_variable(name):
            self._root.createVariable(name, *args, **kwds)

    def set_variable(self, name, *args, **kwds):
        if len(args) not in (0, 1):
            raise ValueError("number of arguments must be 0 or 1")

        attrs = kwds.pop("attrs", {})

        variable = self.data_variable(name)
        for (attr, value) in attrs.items():
            variable.setncattr(attr, value)

        if len(args) > 0:
            array = args[0]
            if "time" in variable.dimensions:
                n_times = self.time_count
                if array.size > 1:
                    variable[n_times, :] = array.flat
                else:
                    variable[n_times] = array[0]
            else:
                variable[:] = array.reshape(variable.shape)

    def data_variable(self, name):
        return self.root.variables[name]

    def _set_mesh_topology(self):
        self._set_topology()
        self._set_mesh_dimensions()
        self._set_time_dimension()
        self._set_mesh_coordinate_data()
        self._set_face_node_connectivity_data()

    def _set_topology(self):
        self.create_variable("mesh", "i8")
        self.set_variable(
            "mesh",
            attrs={
                "cf_role": "mesh_topology",
                "topology_dimension": self.topology_dimension,
                "node_coordinates": " ".join(self.node_coordinates),
                "face_connectivity": self.face_connectivity,
                "face_node_connectivity": self.face_node_connectivity,
                "type": self.type,
            },
        )

    def _set_time_dimension(self):
        if not self.has_dimension("time"):
            self.create_dimension("time", None)

    def _set_coordinate_data(self):
        self._set_mesh_coordinate_data()
        self._set_face_node_connectivity_data()

    def _set_time_variable(
        self, now=None, units="days", reference="0001-01-01 00:00:00 UTC"
    ):
        self.create_variable("time", "f8", ("time",))

        time = self.data_variable("time")
        time.units = " ".join([units, "since", reference])
        time.long_name = "time"

        if now is not None:
            time[self.time_count - 1] = now
        else:
            time[self.time_count - 1] = self.time_count - 1

    def _set_variable_data(self):
        self._set_node_variable_data()
        self._set_face_variable_data()

    def _set_node_variable_data(self):
        point_fields = self.field.get_point_fields()
        for (var_name, array) in point_fields.items():
            self.create_variable(
                var_name,
                _NP_TO_NC_TYPE[str(array.dtype)],
                ["time"] + list(self.node_data_dimensions),
            )
            self.set_variable(
                var_name,
                array,
                attrs={
                    "units": self.field.get_field_units(var_name),
                    "standard_name": var_name,
                    "long_name": var_name,
                    "location": "node",
                    "coordinates": " ".join(self.node_data_dimensions),
                },
            )

    def _set_face_variable_data(self):
        face_fields = self.field.get_cell_fields()
        for (var_name, array) in face_fields.items():
            self.create_variable(
                var_name,
                _NP_TO_NC_TYPE[str(array.dtype)],
                ["time"] + list(self.face_data_dimensions),
            )
            self.set_variable(
                var_name,
                array,
                attrs={
                    "units": self.field.get_field_units(var_name),
                    "standard_name": var_name,
                    "long_name": var_name,
                    "location": "face",
                    "coordinates": " ".join(self.node_data_dimensions),
                },
            )

    def _set_face_node_connectivity_data(self):
        pass


class NetcdfRectilinearField(NetcdfField):
    @property
    def type(self):
        return "rectilinear"

    @property
    def node_coordinates(self):
        return gutils.non_singleton_dimension_names(self.field)

    @property
    def topology_dimension(self):
        return len(gutils.non_singleton_shape(self.field))

    @property
    def node_data_dimensions(self):
        return gutils.non_singleton_dimension_names(self.field)

    @property
    def axis_coordinates(self):
        return gutils.non_singleton_dimension_names(self.field)

    def _set_mesh_dimensions(self):
        field_shape = self.field.get_shape()
        for (name, axis) in zip(self.axis_coordinates, self.field_axes):
            self.create_dimension(name, field_shape[axis])

    def _set_mesh_coordinate_data(self):
        for (name, axis) in zip(self.axis_coordinates, self.field_axes):
            self.create_variable(name, "f8", (name,))
            self.set_variable(
                name,
                self.field.get_axis_coordinates(axis=axis),
                attrs={
                    "units": self.field.get_coordinate_units(axis),
                    "standard_name": self.field.get_coordinate_name(axis),
                    "long_name": self.field.get_coordinate_name(axis),
                    "name": self.field.get_coordinate_name(axis),
                },
            )


class NetcdfStructuredField(NetcdfRectilinearField):
    @property
    def type(self):
        return "structured"

    @property
    def node_data_dimensions(self):
        return gutils.non_singleton_dimension_names(self._field)

    @property
    def node_coordinates(self):
        return gutils.non_singleton_dimension_names(self._field)
        # names = gutils.non_singleton_dimension_names(self._field)
        # return ['node_' + name for name in names]

    def _set_mesh_dimensions(self):
        NetcdfRectilinearField._set_mesh_dimensions(self)

        for name in self.node_coordinates:
            self.create_dimension(name, self.node_count)

    def _set_mesh_coordinate_data(self):
        dims = self.node_data_dimensions
        # for (name, axis) in zip(self.node_coordinates, self.field_axes):
        for (name, axis) in zip(self.node_data_dimensions, self.field_axes):
            self.create_variable(name, "f8", dims)
            self.set_variable(
                name,
                self.field.get_coordinate(axis),
                attrs={
                    "units": self.field.get_coordinate_units(axis),
                    "standard_name": self.field.get_coordinate_name(axis),
                    "long_name": self.field.get_coordinate_name(axis),
                },
            )


class NetcdfUnstructuredField(NetcdfStructuredField):
    @property
    def type(self):
        return "unstructured"

    @property
    def node_coordinates(self):
        names = []
        for axis in range(self.field.get_dim_count()):
            names.append("node_" + self.field.get_coordinate_name(axis))
        return names

    @property
    def topology_dimension(self):
        return self.field.get_dim_count()

    @property
    def node_data_dimensions(self):
        return ("n_node",)
        # dimensions = []
        # for name in self.node_coordinates:
        #    dimensions.append((name, ))
        # return dimensions

    @property
    def face_data_dimensions(self):
        return ("n_face",)

    def _set_mesh_dimensions(self):
        # for name in self.node_coordinates:
        #    self.create_dimension(name, self.node_count)

        self.create_dimension("n_node", self.node_count)
        self.create_dimension("n_face", self.face_count)
        self.create_dimension("n_vertex", self.vertex_count)
        self.create_dimension("n_max_face_nodes", self.field.get_max_vertices())

    def _set_mesh_coordinate_data(self):
        dims = self.node_data_dimensions
        # for (name, axis) in zip(self.node_data_dimensions, self.field_axes):
        # for (name, axis) in zip(self.node_coordinates, self.field_axes):
        for (axis, name) in enumerate(self.node_coordinates):
            self.create_variable(name, "f8", dims)
            self.set_variable(
                name,
                self.field.get_coordinate(axis),
                attrs={
                    "units": self.field.get_coordinate_units(axis),
                    "standard_name": self.field.get_coordinate_name(axis),
                    "long_name": self.field.get_coordinate_name(axis),
                },
            )

    def _set_face_node_connectivity_data(self):
        self.create_variable("face_nodes_connectivity", "i8", ("n_vertex",))
        self.set_variable(
            "face_nodes_connectivity",
            self.field.get_connectivity(),
            attrs={
                "cf_role": "face_node_connectivity",
                "long_name": "Maps every face to its corner nodes.",
                "start_index": 0,
            },
        )

        self.create_variable("face_nodes_offset", "i8", ("n_face",))
        self.set_variable(
            "face_nodes_offset",
            self.field.get_offset(),
            attrs={
                "cf_role": "face_node_offset",
                "long_name": "Maps face index into connectivity array",
            },
        )

        (connectivity, fill_val) = self.field.get_connectivity_as_matrix()

        self.create_variable(
            "face_nodes", "i8", ("n_face", "n_max_face_nodes"), fill_value=fill_val
        )
        self.set_variable(
            "face_nodes",
            connectivity,
            attrs={
                "cf_role": "face_node_connectivity",
                "long_name": "Maps every face to its corner nodes.",
                "start_index": 0,
            },
        )
