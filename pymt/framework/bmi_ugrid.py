from collections import OrderedDict

import numpy as np
import xarray as xr

from landlab.graph import (StructuredQuadGraph,
                           UniformRectilinearGraph,
                           RectilinearGraph)

COORDINATE_NAMES = ["z", "y", "x"]
INDEX_NAMES = ["k", "j", "i"]


def index_names(rank):
    return ["node_" + ind for ind in INDEX_NAMES[-rank:]]


def coordinate_names(rank):
    return ["node_" + d for d in COORDINATE_NAMES[-rank:]]


class _Base(xr.Dataset):
    __slots__ = "bmi", "grid_id", "grid_type", "ndim", "metadata"

    def __init__(self, bmi, grid_id):
        self.bmi = bmi
        self.grid_id = grid_id
        self.grid_type = bmi.grid_type(grid_id)
        self.ndim = bmi.grid_ndim(grid_id)
        self.metadata = OrderedDict()
        super(_Base, self).__init__()

    def set_mesh(self):
        self.update({"mesh": xr.DataArray(data=self.grid_id, attrs=self.metadata)})

    def set_shape(self, shape):
        self.update({"node_shape": xr.DataArray(data=shape, dims=("rank",))})

    def set_spacing(self, spacing):
        self.update({"node_spacing": xr.DataArray(data=spacing, dims=("rank",))})

    def set_origin(self, origin):
        self.update({"node_origin": xr.DataArray(data=origin, dims=("rank",))})

    def get_nodes(self):
        nodes = []
        for dim_name in COORDINATE_NAMES[: -(self.ndim + 1) : -1]:
            data = getattr(self.bmi, "grid_" + dim_name)(self.grid_id)
            nodes.insert(0, data)

        return tuple(nodes)

    def set_nodes(self):
        coords = {}
        for dim_name in COORDINATE_NAMES[: -(self.ndim + 1) : -1]:
            data = getattr(self.bmi, "grid_" + dim_name)(self.grid_id)
            coord = xr.DataArray(
                data=data,
                dims=("node",),
                attrs={"standard_name": dim_name, "units": "m"},
            )
            coords["node_" + dim_name] = coord

        self.update(coords)

    def set_nodes_rectilinear(self, grid_coords):
        coords_at_node = np.meshgrid(*grid_coords, indexing="ij")
        coords = {}
        for axis, dim_name in enumerate(COORDINATE_NAMES[-self.ndim :]):
            coord = xr.DataArray(
                data=coords_at_node[axis].reshape(-1),
                dims=("node",),
                attrs={"standard_name": dim_name, "units": "m"},
            )
            coords["node_" + dim_name] = coord

        self.update(coords)

    def set_connectivity(self, data=None):
        if data is None:
            data = self.bmi.grid_face_nodes(self.grid_id)
        face_node_connectivity = xr.DataArray(
            data=data,
            dims=("vertex",),
            attrs={"standard_name": "Face-node connectivity"},
        )
        self.update({"face_node_connectivity": face_node_connectivity})

    def set_offset(self, data=None):
        if data is None:
            data = self.bmi.grid_face_node_offset(self.grid_id)
        face_node_offset = xr.DataArray(
            data=data,
            dims=("face",),
            attrs={"standard_name": "Offset to face-node connectivity"},
        )
        self.update({"face_node_offset": face_node_offset})


class Scalar(_Base):
    __slots__ = ()

    def __init__(self, *args):
        super(Scalar, self).__init__(*args)

        if self.ndim != 0:
            raise ValueError("scalar must be rank 0")

        self.metadata = OrderedDict(
            [
                ("cf_role", "grid_topology"),
                ("long_name", "scalar value"),
                ("topology_dimension", self.ndim),
                ("type", self.grid_type),
            ]
        )
        self.set_mesh()


class Vector(_Base):
    __slots__ = ()

    def __init__(self, *args):
        super(Vector, self).__init__(*args)

        if self.ndim != 1:
            raise ValueError("vector must be rank 1")

        self.metadata = OrderedDict(
            [
                ("cf_role", "grid_topology"),
                ("long_name", "vector value"),
                ("topology_dimension", self.ndim),
                ("type", self.grid_type),
            ]
        )
        self.set_mesh()


class Points(_Base):
    __slots__ = ()

    def __init__(self, *args):
        super(Points, self).__init__(*args)

        self.metadata = OrderedDict(
            [
                ("cf_role", "mesh_topology"),
                ("long_name", "Topology data of 2D unstructured points"),
                ("topology_dimension", self.ndim),
                ("node_coordinates", "node_x node_y"),
                ("type", self.grid_type),
            ]
        )
        self.set_mesh()
        self.set_nodes()


class Unstructured(_Base):
    __slots__ = ()

    def __init__(self, *args):
        super(Unstructured, self).__init__(*args)

        self.metadata = OrderedDict(
            [
                ("cf_role", "mesh_topology"),
                ("long_name", "Topology data of 2D unstructured points"),
                ("topology_dimension", self.ndim),
                ("node_coordinates", "node_x node_y"),
                ("type", self.grid_type),
            ]
        )
        self.set_mesh()
        self.set_nodes()
        self.set_connectivity()
        self.set_offset()


class StructuredQuadrilateral(_Base):
    __slots__ = ()

    def __init__(self, *args):
        super(StructuredQuadrilateral, self).__init__(*args)

        if self.ndim < 1 or self.ndim > 3:
            raise ValueError("structured_quadrilateral grid must be rank 1, 2, or 3")

        shape = self.bmi.grid_shape(self.grid_id)

        self.metadata = OrderedDict(
            [
                ("cf_role", "grid_topology"),
                (
                    "long_name",
                    "Topology data of {}D structured quadrilateral".format(self.ndim),
                ),
                ("topology_dimension", self.ndim),
                ("node_coordinates", " ".join(coordinate_names(self.ndim))),
                ("node_dimensions", " ".join(index_names(self.ndim))),
                ("type", self.grid_type),
            ]
        )
        self.set_mesh()
        self.set_shape(shape)
        nodes = self.get_nodes()
        self.set_nodes()

        graph = StructuredQuadGraph(nodes, shape=tuple(shape))

        self.set_connectivity(data=graph.nodes_at_patch.reshape((-1,)))
        self.set_offset(
            data=np.arange(1, graph.number_of_patches + 1, dtype=np.int32) * 4
        )


class Rectilinear(_Base):
    __slots__ = ()

    def __init__(self, *args):
        super(Rectilinear, self).__init__(*args)

        if self.ndim < 1 or self.ndim > 3:
            raise ValueError("rectilinear grid must be rank 1, 2, or 3")

        shape = self.bmi.grid_shape(self.grid_id)

        self.metadata = OrderedDict(
            [
                ("cf_role", "grid_topology"),
                (
                    "long_name",
                    "Topology data of {}D structured quadrilateral".format(self.ndim),
                ),
                ("topology_dimension", self.ndim),
                ("node_coordinates", " ".join(coordinate_names(self.ndim))),
                ("node_dimensions", " ".join(index_names(self.ndim))),
                ("type", self.grid_type),
            ]
        )
        self.set_mesh()
        self.set_shape(shape)
        nodes = self.get_nodes()
        self.set_nodes_rectilinear(nodes)

        graph = RectilinearGraph(nodes)

        self.set_connectivity(data=graph.nodes_at_patch.reshape((-1,)))
        self.set_offset(
            data=np.arange(1, graph.number_of_patches + 1, dtype=np.int32) * 4
        )


class UniformRectilinear(_Base):
    __slots__ = ()

    def __init__(self, *args):
        super(UniformRectilinear, self).__init__(*args)

        if self.ndim < 1 or self.ndim > 3:
            raise ValueError("uniform_rectangular grid must be rank 1, 2, or 3")

        shape = self.bmi.grid_shape(self.grid_id)
        spacing = self.bmi.grid_spacing(self.grid_id)
        origin = self.bmi.grid_origin(self.grid_id)

        self.metadata = OrderedDict(
            [
                ("cf_role", "grid_topology"),
                (
                    "long_name",
                    "Topology data of {}D structured quadrilateral".format(self.ndim),
                ),
                ("topology_dimension", self.ndim),
                ("node_coordinates", " ".join(coordinate_names(self.ndim))),
                ("node_dimensions", " ".join(index_names(self.ndim))),
                ("node_spacing", "node_spacing"),
                ("node_origin", "node_origin"),
                ("type", self.grid_type),
            ]
        )
        self.set_mesh()
        self.set_shape(shape)
        self.set_spacing(spacing)
        self.set_origin(origin)

        grid_coords = []
        for dim in range(self.ndim):
            grid_coords.append(
                np.arange(shape[dim], dtype=float) * spacing[dim] + origin[dim]
            )
        self.set_nodes_rectilinear(grid_coords)

        graph = UniformRectilinearGraph(shape, spacing=spacing, origin=origin)

        self.set_connectivity(data=graph.nodes_at_patch.reshape((-1,)))
        self.set_offset(
            data=np.arange(1, graph.number_of_patches + 1, dtype=np.int32) * 4
        )


def dataset_from_bmi_grid(bmi, grid_id):
    grid_type = bmi.grid_type(grid_id)
    if grid_type == "points":
        grid = Points(bmi, grid_id)
    elif grid_type == "uniform_rectilinear":
        grid = UniformRectilinear(bmi, grid_id)
    elif grid_type == "structured_quadrilateral":
        grid = StructuredQuadrilateral(bmi, grid_id)
    elif grid_type == "scalar":
        grid = Scalar(bmi, grid_id)
    elif grid_type.startswith("unstructured"):
        grid = Unstructured(bmi, grid_id)
    elif grid_type == "vector":
        grid = Vector(bmi, grid_id)
    elif grid_type == "rectilinear":
        grid = Rectilinear(bmi, grid_id)
    else:
        raise ValueError("grid type not understood ({gtype})".format(gtype=grid_type))

    return grid
