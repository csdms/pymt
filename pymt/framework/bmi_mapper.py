#! /usr/bin/env python
import warnings

import numpy as np

try:
    import ESMF as esmf
except ImportError:
    esmf = None


REGRID_METHODS = {}
UNMAPPED_ACTIONS = {}

if esmf is not None:
    REGRID_METHODS.update(
        {
            "bilinear": esmf.RegridMethod.BILINEAR,
            "nearest": esmf.RegridMethod.NEAREST_STOD,
            "conserve": esmf.RegridMethod.CONSERVE,
        }
    )
    UNMAPPED_ACTIONS.update(
        {"pass": esmf.UnmappedAction.IGNORE, "raise": esmf.UnmappedAction.ERROR}
    )


def ravel_jaggedarray(array):
    values_per_row = np.sum(array >= 0, axis=1)

    raveled_array = np.empty(values_per_row.sum(), dtype=array.dtype)
    offset = 0
    for row, n_values in zip(array, values_per_row):
        raveled_array[offset : offset + n_values] = row[row >= 0]
        offset += n_values

    return raveled_array, values_per_row


def bmi_as_esmf_mesh(bmi_grid):
    xy_at_node = np.vstack((bmi_grid.node_x.values, bmi_grid.node_y.values)).T.copy()

    if "face_node_connectivity" in bmi_grid:
        nodes_at_patch = bmi_grid.face_node_connectivity.values
        nodes_per_patch = np.diff(
            np.concatenate(([0], bmi_grid.face_node_offset.values))
        )
    else:
        nodes_at_patch = None
        nodes_per_patch = None

    return as_esmf_mesh(xy_at_node, nodes_at_patch, nodes_per_patch)

    # return as_esmf_mesh(xy_at_node, np.astype(nodes_at_patch, dtype=np.int32),
    #                     np.astype(nodes_per_patch, dtype=np.int32))


def as_esmf_mesh(xy_of_node, nodes_at_patch=None, nodes_per_patch=None):
    mesh = esmf.Mesh(parametric_dim=2, spatial_dim=2)

    n_nodes = len(xy_of_node)

    node_ids = np.arange(1, n_nodes + 1, dtype=np.int32)
    node_owner = np.zeros(n_nodes, dtype=np.int32)

    mesh.add_nodes(n_nodes, node_ids, xy_of_node, node_owner)

    if nodes_at_patch is not None:
        if nodes_at_patch.ndim == 2:
            n_faces = len(nodes_at_patch)
        else:
            n_faces = len(nodes_per_patch)

        face_ids = np.arange(1, n_faces + 1, dtype=np.int32)

        if nodes_at_patch.ndim == 2:
            face_conn, nodes_per_face = ravel_jaggedarray(nodes_at_patch)
        else:
            face_conn, nodes_per_face = nodes_at_patch, nodes_per_patch

        face_conn = face_conn.astype(dtype=np.int32, copy=False)
        nodes_per_face = nodes_per_face.astype(dtype=np.int32, copy=False)

        if np.all((nodes_per_face == 3) | (nodes_per_face == 4)):
            face_types = np.full(n_faces, -1, dtype=np.int32)
            face_types[np.where(nodes_per_face == 3)] = esmf.MeshElemType.TRI
            face_types[np.where(nodes_per_face == 4)] = esmf.MeshElemType.QUAD

            mesh.add_elements(n_faces, face_ids, face_types, face_conn)
        else:
            warnings.warn("mesh contains non-triangular or quadrilateral elements")

    return mesh


def as_esmf_field(mesh, field_name, data=None, at="node"):
    if at == "node":
        meshloc = esmf.MeshLoc.NODE
    elif at == "cell":
        meshloc = esmf.MeshLoc.ELEMENT
    else:
        raise ValueError("'at' location not understood (must be 'cell' or 'node')")

    field = esmf.Field(mesh, field_name, meshloc=meshloc)
    if data is not None:
        np.copyto(field.data, data.reshape(field.data.shape))

    return field


def graph_as_esmf(graph, field_name, data=None, at="node"):
    mesh = as_esmf_mesh(graph.xy_of_node, graph.nodes_at_patch)
    field = as_esmf_field(mesh, field_name, data=data, at=at)

    return field


def run_regridding(srcfield, dstfield, method="nearest", unmapped="pass"):
    """run_regridding(source_field, destination_field, method=ESMP_REGRIDMETHOD_CONSERVE, unmapped=ESMP_UNMAPPEDACTION_ERROR)

    **PRECONDITIONS:**
        Two ESMP_Fields have been created and a regridding operation is desired from 'srcfield' to 'dstfield'.
    **POSTCONDITIONS:**
        An ESMP regridding operation has set the data on 'dstfield'.
    """
    # method = kwds.get('method', ESMF.RegridMethod.NEAREST_STOD)
    # method = kwds.get('method', ESMF.RegridMethod.BILINEAR)
    # unmapped = kwds.get('unmapped', ESMF.UnmappedAction.IGNORE)
    # method = kwds.get('method', ESMF.RegridMethod.CONSERVE)
    # unmapped = kwds.get('unmapped', ESMF.UnmappedAction.ERROR)

    try:
        method = REGRID_METHODS[method]
    except KeyError:
        raise ValueError("regrid method not understood")
    try:
        unmapped = UNMAPPED_ACTIONS[unmapped]
    except KeyError:
        raise ValueError("unmapped action not understood")

    # call the regridding functions
    masked_values = np.array([-9999.0])
    regridder = esmf.Regrid(
        srcfield,
        dstfield,
        regrid_method=method,
        unmapped_action=unmapped,
        src_mask_values=masked_values,
        dst_mask_values=masked_values,
    )
    dstfield = regridder(srcfield, dstfield)

    return dstfield


class GridMapperMixIn:
    def _esmf_mesh_by_id(self, gid):
        try:
            self._esmf_mesh
        except AttributeError:
            self._esmf_mesh = dict()

        try:
            self._esmf_mesh[gid]
        except KeyError:
            self._esmf_mesh[gid] = bmi_as_esmf_mesh(self.grid[gid])

        return self._esmf_mesh[gid]

    def _esmf_field_by_id(self, gid, name=None, at="node"):
        name = name or "generic"

        try:
            self._esmf_field
        except AttributeError:
            self._esmf_field = dict()

        _id = "{gid}.{name}@{at}".format(gid=gid, name=name, at=at)

        try:
            self._esmf_field[_id]
        except KeyError:
            self._esmf_field[_id] = as_esmf_field(
                self._esmf_mesh_by_id(gid), name, at=at
            )

        return self._esmf_field[_id]

    def regrid(self, name, **kwds):
        """Regrid values from one grid to another.

        Parameters
        ----------
        name : str
            Name of the values to regrid.
        to : bmi_like, optional
            BMI object onto which to map values. If not provided, map
            values onto one of the object's own grids.
        to_name : str, optional
            Name of the value to map onto. If not provided, use *name*.

        Returns
        -------
        ndarray
            The regridded values.
        """
        dst = kwds.pop("to", self)
        dst_name = kwds.pop("to_name", name)

        data = self.get_value(name, **kwds)

        if esmf is not None:
            src_field = self._esmf_field_by_id(self.var[name].grid, at="node")
            dst_field = dst._esmf_field_by_id(dst.var[dst_name].grid, at="node")

            np.copyto(src_field.data, data.reshape(src_field.data.shape))

            run_regridding(src_field, dst_field)

            return dst_field.data
        else:
            return data

    def map_to(self, name, **kwds):
        """Map values to another grid.

        Parameters
        ----------
        name : str
            Name of values to push.
        """
        destination = kwds.pop("destination", self)
        at = kwds.pop("at", name)
        data = self.regrid(name, to=destination, to_name=at, **kwds)
        destination.set_value(at, data)

    def set_value(self, name, *args, **kwds):
        """Set values for a variable.
        set_value(name, value)
        set_value(name, mapfrom=self, nomap=None)

        Parameters
        ----------
        name : str
            Name of the destination values.
        """
        if len(args) == 1:
            return super().set_value(name, *args)

        mapfrom = kwds.pop("mapfrom", self)
        nomap = kwds.pop("nomap", None)
        try:
            value, source = mapfrom
        except TypeError:
            value, source = name, mapfrom

        if nomap is not None:
            orig = self.get_value(name)

        data = source.regrid(value, to=self, to_name=name, **kwds)

        if nomap is not None:
            data[nomap] = orig[nomap]

        super().set_value(name, data)

    def map_value(self, name, **kwds):
        """Map values from another grid.

        Parameters
        ----------
        name : str
            Name of values to map to.
        mapfrom : tuple or bmi_like, optional
            BMI object from which values are mapped from. This can also be
            a tuple of *(name, bmi)*, where *name* is the variable of the
            source grid and *bmi* is the bmi-like source. If not provided,
            use *self*.
        nomap : narray of bool, optional
            Values in the destination grid to not map.
        """
        mapfrom = kwds.pop("mapfrom", self)
        nomap = kwds.pop("nomap", None)
        try:
            value, source = mapfrom
        except TypeError:
            value, source = name, mapfrom

        if nomap is not None:
            orig = self.get_value(name)

        data = source.regrid(value, to=self, to_name=name, **kwds)

        if nomap is not None:
            data[nomap] = orig[nomap]

        self.set_value(name, data)
