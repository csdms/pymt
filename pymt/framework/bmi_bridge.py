"""Bridge between BMI and a PyMT component."""
import ctypes
import json
import os
from pprint import pformat

import numpy as np
import yaml
import gimli

from deprecated import deprecated

from ..utils import as_cwd
from ..errors import BmiError
from ..units import transform_azimuth_to_math, transform_math_to_azimuth
from .bmi_docstring import bmi_docstring
from .bmi_mapper import GridMapperMixIn
from .bmi_plot import quick_plot
from .bmi_setup import SetupMixIn
from .bmi_timeinterp import BmiTimeInterpolator
from .bmi_ugrid import dataset_from_bmi_grid


UNITS = gimli.units


class DataValues:
    def __init__(self, bmi, name):
        self._bmi = bmi
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def units(self):
        return self._bmi.var_units(self.name)

    @property
    def grid(self):
        if self.location == "none":
            return None
        return self._bmi.var_grid(self.name)

    @property
    def size(self):
        return self._bmi.var_size(self.name)

    @property
    def type(self):
        return self._bmi.var_type(self.name)

    @property
    def intent(self):
        return self._bmi.var_intent(self.name)

    @property
    def location(self):
        return self._bmi.var_grid_loc(self.name)

    @property
    def data(self):
        return self.values()

    def values(self, **kwds):
        if "out" in self.intent:
            return self._bmi.get_value(self.name, **kwds)
        else:
            raise ValueError("not an output var")

    def __repr__(self):
        return str(self)

    def __str__(self):
        return """
<DataValues>
{dtype} {name}({location})
Attributes:
    units: {units}
    grid: {grid}
    intent: {intent}
    location: {location}
""".format(
            dtype=self.type,
            name=self.name,
            units=self.units,
            grid=self.grid,
            intent=self.intent,
            location=self.location,
        ).strip()


class _BmiCapV1:

    """Add methods for backward compatibility."""

    @staticmethod
    def _call_bmi(func, *args):
        rtn = func(*args)

        try:
            status, val = rtn
        except TypeError:
            status, val = rtn, None

        if status != 0:
            raise BmiError(func.__name__ + pformat(args), status)
        else:
            return val

    @deprecated(reason="use get_grid_number_of_vertices")
    def get_grid_vertex_count(self, grid):
        return _BmiCapV1._call_bmi(self.bmi.get_grid_vertex_count, grid)

    @deprecated(reason="use get_grid_number_of_faces")
    def get_grid_face_count(self, grid):
        return _BmiCapV1._call_bmi(self.bmi.get_grid_face_count, grid)

    @deprecated(reason="use get_grid_face_node_connectivity")
    def get_grid_connectivity(self, grid, out=None):
        if out is None:
            out = np.empty(self.grid_vertex_count(grid), dtype=ctypes.c_int)
        return _BmiCapV1._call_bmi(self.bmi.get_grid_connectivity, grid, out)

    @deprecated(reason="use get_grid_face_node_offset")
    def get_grid_offset(self, grid, out=None):
        if out is None:
            out = np.empty(self.grid_face_count(grid), dtype=ctypes.c_int)
        return _BmiCapV1._call_bmi(self.bmi.get_grid_offset, grid, out)


class _BmiCapV2:
    @deprecated(reason="use get_grid_number_of_vertices")
    def get_grid_vertex_count(self, grid):
        return self.grid_vertex_count(grid)

    @deprecated(reason="use get_grid_number_of_faces")
    def get_grid_face_count(self, grid):
        return self.grid_number_of_faces(grid)

    @deprecated(reason="use get_grid_face_node_connectivity")
    def get_grid_connectivity(self, grid, out=None):
        return self.grid_face_node_connectivity(grid, out=out)

    @deprecated(reason="use get_grid_face_node_offset")
    def get_grid_offset(self, grid, out=None):
        return self.grid_face_node_offset(grid, out=out)


class DeprecatedMethods:
    @deprecated(reason="use grid_ndim")
    def get_grid_rank(self, grid):
        return self.get_grid_ndim(grid)

    @deprecated(reason="use grid_ndim")
    def get_grid_ndim(self, grid):
        return self.grid_ndim(grid)
        # return self.bmi.get_grid_rank(grid)

    @deprecated(reason="use grid_dim")
    def get_grid_dim(self, grid, dim):
        return self.grid_dim(grid, dim)
        # return getattr(self, self.NUMBER_OF_ELEMENTS[dim])(grid)

    @deprecated(reason="use grid_node_count")
    def get_grid_size(self, grid):
        return self.grid_node_count(grid)

    @deprecated(reason="use grid_type")
    def get_grid_type(self, grid):
        return self.grid_type(grid)
        # return self.bmi.get_grid_type(grid)

    @deprecated(reason="use grid_shape")
    def get_grid_shape(self, grid, out=None):
        return self.grid_shape(grid, out=out)

    @deprecated(reason="use grid_spacing")
    def get_grid_spacing(self, grid, out=None):
        return self.grid_spacing(grid, out=out)

    @deprecated(reason="use grid_origin")
    def get_grid_origin(self, grid, out=None):
        return self.grid_origin(grid, out=out)

    @deprecated(reason="use grid_node_count")
    def get_grid_number_of_nodes(self, grid):
        return self.bmi.get_grid_size(grid)

    @deprecated(reason="use grid_edge_count")
    def get_grid_number_of_edges(self, grid):
        return self.grid_edge_count(grid)
        # return self.bmi.get_grid_edge_count(grid)

    @deprecated(reason="use grid_vertex_count")
    def get_grid_number_of_vertices(self, grid):
        return self.grid_vertex_count(grid)
        # return self.get_grid_nodes_per_face(grid).sum()

    @deprecated(reason="use grid_face_count")
    def get_grid_number_of_faces(self, grid):
        return self.grid_face_count(grid)
        # return self.bmi.get_grid_face_count(grid)
        # return self.bmi.get_grid_number_of_faces(grid)

    @deprecated(reason="use grid_face_node_connectivity")
    def get_grid_face_node_connectivity(self, grid, out=None):
        return self.grid_face_node_connectivity(grid, out=out)

    @deprecated(reason="use grid_face_nodes")
    def get_grid_face_nodes(self, grid, out=None):
        return self.grid_face_nodes(grid, out=out)

    @deprecated(reason="use grid_face_node_offset")
    def get_grid_face_node_offset(self, grid, out=None):
        return self.grid_face_node_offset(grid, out=out)

    @deprecated(reason="use grid_nodes_per_face")
    def get_grid_nodes_per_face(self, grid, out=None):
        return self.grid_nodes_per_face(grid, out=out)

    @deprecated(reason="use grid_x")
    def get_grid_x(self, grid, out=None):
        return self.grid_x(grid, out=out)

    @deprecated(reason="use grid_y")
    def get_grid_y(self, grid, out=None):
        return self.grid_y(grid, out=out)

    @deprecated(reason="use grid_z")
    def get_grid_z(self, grid, out=None):
        return self.grid_z(grid, out=out)

    @deprecated(reason="use var_intent")
    def get_var_intent(self, name):
        return self.var_intent(name)

    @deprecated(reason="use var_location")
    def get_var_location(self, name):
        return self.var_location(name)

    @deprecated(reason="use var_grid_loc")
    def get_var_grid_loc(self, name):
        return self.var_loc(name)

    @deprecated(reason="use var_grid")
    def get_var_grid(self, name):
        return self.var_grid(name)

    @deprecated(reason="use var_itemsize")
    def get_var_itemsize(self, name):
        return self.var_itemsize(name)

    @deprecated(reason="use var_nbytes")
    def get_var_nbytes(self, name):
        return self.var_nbytes(name)

    @deprecated(reason="use var_type")
    def get_var_type(self, name):
        return self.var_type(name)

    @deprecated(reason="use var_units")
    def get_var_units(self, name):
        return self.var_units(name)


class _BmiCap(DeprecatedMethods):
    def __init__(self):
        self._bmi = self._cls()
        self._initialized = False
        self._grid = dict()
        self._var = dict()
        self._time_units = None
        self._initdir = None
        super().__init__()

    @property
    def bmi(self):
        return self._bmi

    @property
    def name(self):
        return self.get_component_name()

    @property
    def grid(self):
        return self._grid

    @property
    def var(self):
        return self._var

    @property
    def initdir(self):
        return self._initdir

    def _grid_ids(self):
        grids = set()
        for var in set(self.input_var_names + self.output_var_names):
            if self.var_grid(var) is not None:
                grids.add(self.var_grid(var))
        return tuple(grids)

    def get_component_name(self):
        return self.bmi.get_component_name()

    def initialize(self, fname=None, dir="."):  # pylint: disable=redefined-builtin
        """Initialize the model.

        Parameters
        ----------
        fname : str
            Name of initialization file.
        dir : str
            Path to folder in which to run initialization.
        """
        self._initdir = os.path.abspath(dir)
        with as_cwd(self.initdir):
            self.bmi.initialize(fname or "")
            self._initialized = True

        for grid_id in self._grid_ids():
            self._grid[grid_id] = dataset_from_bmi_grid(self, grid_id)

        for name in set(self.output_var_names + self.input_var_names):
            self._var[name] = DataValues(self, name)

    def update(self):
        with as_cwd(self.initdir):
            return self.bmi.update()

    def finalize(self):
        with as_cwd(self.initdir):
            self._initialized = False
            return self.bmi.finalize()

    def set_value(self, name, val):
        val = np.asarray(val).reshape((-1,))
        return self.bmi.set_value(name, val)

    def get_value(self, name, out=None, units=None, angle=None, at=None, method=None):
        if out is None:
            # grid = self.var_grid(name)
            dtype = self.var_type(name)
            if dtype == "":
                raise ValueError(f"{name} not understood")
            n_items = self.var_nbytes(name) // self.var_itemsize(name)
            # loc = self.var_grid_loc(name)
            out = np.empty(n_items, dtype=dtype)
            # out = np.empty(self.grid_dim(grid, loc), dtype=dtype)
            # out = np.empty(self.grid_dim(grid, loc), dtype=dtype)

        self.bmi.get_value(name, out)

        if name in self._interpolators and at is not None:
            out[:] = self._interpolators[name].interpolate(at)

        # from_units = Units(self.var_units(name))
        # if units is not None:
        #     to_units = Units(units)
        # else:
        #     to_units = from_units

        # if units is not None and from_units != to_units:
        #     Units.conform(out, from_units, to_units, inplace=True)

        if units is not None:
            convert = UNITS.Unit(self.var_units(name)).to(UNITS[units])
            # convert = UnitConverter(self.var_units(name), units)
            convert(out, out=out)

        # if units is not None:
        #     try:
        #         from_units = self.var_units(name)
        #     except AttributeError, NotImplementedError:
        #         pass
        #     else:
        #         Units.conform(out, Units(from_units), Units(units),
        #                       inplace=True)

        if angle not in ("azimuth", "math", None):
            raise ValueError("angle not understood")

        if units is not None:
            if angle == "azimuth" and "azimuth" not in name:
                transform_math_to_azimuth(out, units)
            elif angle == "math" and "azimuth" in name:
                transform_azimuth_to_math(out, units)

        return out

    def get_value_ptr(self, name):
        return self.bmi.get_value_ptr(name)

    def grid_ndim(self, grid):
        return self.bmi.get_grid_rank(grid)

    NUMBER_OF_ELEMENTS = {
        "node": "grid_node_count",
        "edge": "grid_edge_count",
        "face": "grid_face_count",
        "vertex": "grid_vertex_count",
        # "node": "grid_number_of_nodes",
        # "edge": "grid_number_of_edges",
        # "face": "grid_number_of_faces",
        # "vertex": "grid_number_of_vertices",
    }

    def grid_dim(self, grid, dim):
        return getattr(self, self.NUMBER_OF_ELEMENTS[dim])(grid)

    def grid_type(self, grid):
        return self.bmi.get_grid_type(grid)

    def grid_shape(self, grid, out=None):
        if out is None:
            out = np.empty(self.grid_ndim(grid), dtype=ctypes.c_int)
        self.bmi.get_grid_shape(grid, out)
        return out

    def grid_spacing(self, grid, out=None):
        if out is None:
            out = np.empty(self.grid_ndim(grid), dtype=ctypes.c_double)
        self.bmi.get_grid_spacing(grid, out)
        return out

    def grid_origin(self, grid, out=None):
        if out is None:
            out = np.empty(self.grid_ndim(grid), dtype=ctypes.c_double)
        self.bmi.get_grid_origin(grid, out)
        return out

    def grid_face_node_connectivity(self, grid, out=None):
        if out is None:
            out = np.empty(self.grid_vertex_count(grid), dtype=ctypes.c_int)
        self.bmi.get_grid_face_nodes(grid, out)
        return out

    def grid_face_nodes(self, grid, out=None):
        if self.grid_face_count(grid) > 0:
            if out is None:
                out = np.empty(self.grid_vertex_count(grid), dtype=ctypes.c_int)
            self.bmi.get_grid_face_nodes(grid, out)
        return out

    def grid_face_node_offset(self, grid, out=None):
        nodes_per_face = self.grid_nodes_per_face(grid, out=out)
        return np.cumsum(nodes_per_face, out=out)

    def grid_nodes_per_face(self, grid, out=None):
        if self.grid_face_count(grid) > 0:
            if out is None:
                out = np.empty(self.grid_face_count(grid), dtype=ctypes.c_int)
            self.bmi.get_grid_nodes_per_face(grid, out)
        return out

    def grid_x(self, grid, out=None):
        if out is None:
            if self.grid_type(grid) == "rectilinear":
                out = np.empty(self.grid_shape(grid)[-1], dtype=float)
            else:
                out = np.empty(self.grid_node_count(grid), dtype=float)
        self.bmi.get_grid_x(grid, out)
        return out

    def grid_y(self, grid, out=None):
        if out is None:
            if self.grid_type(grid) == "rectilinear":
                out = np.empty(self.grid_shape(grid)[-2], dtype=float)
            else:
                out = np.empty(self.grid_node_count(grid), dtype=float)
        self.bmi.get_grid_y(grid, out)
        return out

    def grid_z(self, grid, out=None):
        if out is None:
            if self.grid_type(grid) == "rectilinear":
                shape = self.grid_shape(grid)
                try:
                    zdim = shape[-3]
                except IndexError:
                    zdim = 1
                out = np.empty(zdim, dtype=float)
            else:
                out = np.empty(self.grid_node_count(grid), dtype=float)

        self.bmi.get_grid_z(grid, out)
        return out

    def grid_node_count(self, grid):
        try:
            self.bmi.get_grid_node_count
        except AttributeError:
            return self.bmi.get_grid_size(grid)
            # return self.bmi.get_grid_number_of_nodes(grid)
        else:
            return self.bmi.get_grid_node_count(grid)

    def grid_edge_count(self, grid):
        try:
            self.bmi.get_grid_edge_count
        except AttributeError:
            return self.bmi.get_grid_number_of_edges(grid)
        else:
            return self.bmi.get_grid_edge_count(grid)

    def grid_face_count(self, grid):
        try:
            self.bmi.get_grid_face_count
        except AttributeError:
            return self.bmi.get_grid_number_of_faces(grid)
        else:
            return self.bmi.get_grid_face_count(grid)

    def grid_vertex_count(self, grid):
        return (
            self.grid_nodes_per_face(grid).sum()
            if self.grid_face_count(grid) > 0
            else 0
        )
        # return self.grid_nodes_per_face(grid).sum()

    @property
    def input_var_names(self):
        return tuple(self.bmi.get_input_var_names())

    def get_input_var_names(self):
        return self.input_var_names

    @property
    def output_var_names(self):
        return tuple(self.bmi.get_output_var_names())

    def get_output_var_names(self):
        return self.output_var_names

    @property
    def time_units(self):
        return self._time_units or self.bmi.get_time_units()
        # return self.get_time_units()

    @time_units.setter
    def time_units(self, new_units):
        self._time_units = new_units
        self._time_converter = UNITS.Unit(self.bmi.get_time_units()).to(
            UNITS[new_units]
        )
        # self._time_converter = UnitConverter(self.bmi.get_time_units(), new_units)

    # def get_time_units(self):
    #     return self.bmi.get_time_units()

    @property
    def time(self):
        return self._conform_time(self.bmi.get_current_time())

    def _conform_time(self, time):
        try:
            self._time_converter
        except AttributeError:
            return time
        else:
            return self._time_converter(time)

        # try:
        #     self._time_converter
        # except AttributeError:
        #     self._time_converter = UnitConverter(self.bmi.get_time_units())
        # return self._time_converter(time, self.time_units)

    @property
    def start_time(self):
        return self._conform_time(self.bmi.get_start_time())

    @property
    def end_time(self):
        return self._conform_time(self.bmi.get_end_time())

    @property
    def time_step(self):
        return self._conform_time(self.bmi.get_time_step())

    # def get_current_time(self, units=None):
    #     time = self.bmi.get_current_time()
    #     return self.time_in(time, units)

    # def get_start_time(self, units=None):
    #     time = self.bmi.get_start_time()
    #     return self.time_in(time, units)

    # def get_end_time(self, units=None):
    #     time = self.bmi.get_end_time()
    #     return self.time_in(time, units)

    # def get_time_step(self, units=None):
    #     time = self.bmi.get_time_step()
    #     return self.time_in(time, units)

    def time_in(self, time, units):
        # if units is None:
        #     units = self.time_units
        #     # return time

        # try:
        #     units_str = self.time_units
        #     # units_str = self.time_units
        # except (AttributeError, NotImplementedError):
        #     pass
        # else:
        #     from_units = Units(units_str)
        #     to_units = Units(units)

        #     if not from_units.equals(to_units):
        #         time = Units.conform(time, from_units, to_units)

        try:
            self.time_units
        except (AttributeError, NotImplementedError):
            return time

        if units is not None:
            convert = UNITS.Unit(self.time_units).to(UNITS[units])
            # convert = UnitConverter(self.time_units, units)
            time = convert(time)

        return time

    def time_from(self, time, units):
        # if units is None:
        #     return time

        # try:
        #     # units_str = self.time_units
        #     units_str = self.time_units
        # except (AttributeError, NotImplementedError):
        #     pass
        # else:
        #     to_units = Units(units_str)
        #     from_units = Units(units)

        #     if not from_units.equals(to_units):
        #         time = Units.conform(time, from_units, to_units)

        try:
            self.time_units
        except (AttributeError, NotImplementedError):
            return time

        if units is not None:
            convert = UNITS.Unit(units).to(UNITS[self.time_units])
            # convert = UnitConverter(units, self.time_units)
            time = convert(time)

        return time

    def var_intent(self, name):
        intent = ""
        if name in self.input_var_names:
            intent += "in"
        if name in self.output_var_names:
            intent += "out"
        return intent

    def var_location(self, name):
        return self.var_grid_loc(name)

    def var_grid_loc(self, name):
        try:
            self.bmi.get_var_location
        except AttributeError:
            return "node"
        else:
            return self.bmi.get_var_location(name)

    def var_grid(self, name):
        if self.var_location(name) == "none":
            return None
        return self.bmi.get_var_grid(name)

    def var_itemsize(self, name):
        return self.bmi.get_var_itemsize(name)

    def var_nbytes(self, name):
        return self.bmi.get_var_nbytes(name)

    def var_type(self, name):
        return self.bmi.get_var_type(name)

    def var_units(self, name):
        units = self.bmi.get_var_units(name)
        if units == "-":
            return ""
        else:
            return units

    def as_dict(self):
        vars_ = {}
        grid_ids = set()
        for var in set(self.input_var_names + self.output_var_names):
            var_desc = {
                # 'name': var,
                "intent": "",
                "units": self.var_units(var),
                "dtype": self.var_type(var),
                "itemsize": self.var_itemsize(var),
                "nbytes": self.var_nbytes(var),
                "grid": self.var_grid(var),
            }
            vars_[var] = var_desc

            if var in self.input_var_names:
                var_desc["intent"] += "in"
            if var in self.output_var_names:
                var_desc["intent"] += "out"
            # vars_.append(var_desc)
            grid_ids.add(var_desc["grid"])
        # vars_.sort(cmp=lambda a, b: cmp(a['name'], b['name']))

        grids = {}
        for grid_id in grid_ids:
            grid_desc = {
                # 'id': grid_id,
                "rank": self.get_grid_ndim(grid_id),
                "size": self.grid_node_count(grid_id),
                "type": self.get_grid_type(grid_id),
            }
            grids[grid_id] = grid_desc
            # grids.append(grid_desc)
        # grids.sort(cmp=lambda a, b: cmp(a['id'], b['id']))

        in_vars = list(self.input_var_names)
        out_vars = list(self.output_var_names)
        in_vars.sort()
        out_vars.sort()

        times = {
            "start": self.start_time,
            "end": self.end_time,
            "current": self.time,
            # 'time_step': self.get_time_step(),
            "units": self.time_units,
        }
        return {
            "name": self.name,
            "input_var_names": in_vars,
            "output_var_names": out_vars,
            "vars": vars_,
            "grids": grids,
            "times": times,
        }

    def as_yaml(self):
        return yaml.dump(self.as_dict(), default_flow_style=False)

    def as_json(self):
        return json.dumps(self.as_dict())

    def quick_plot(self, name, **kwds):
        return quick_plot(self, name, **kwds)

    def __str__(self):
        return yaml.dump(
            {
                "name": self.name,
                "input_var_names": list(self.input_var_names),
                "output_var_names": list(self.output_var_names),
            },
            default_flow_style=False,
        )


class BmiCap(GridMapperMixIn, _BmiCap, BmiTimeInterpolator, SetupMixIn):
    pass


def bmi_factory(cls):
    class BmiWrapper(BmiCap):
        # __doc__ = bmi_docstring(cls.__name__.split('.')[-1])
        __doc__ = bmi_docstring(cls)
        _cls = cls

        def __str__(self):
            return f"{cls.__name__}"

        def __repr__(self):
            return f"<{cls.__name__}()>"

    BmiWrapper.__name__ = cls.__name__
    return BmiWrapper
