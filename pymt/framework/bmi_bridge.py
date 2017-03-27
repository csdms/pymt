from pprint import pformat

import numpy as np
from scipy.interpolate import interp1d
import xarray as xr
import json
import yaml

from cfunits import Units

from scripting.contexts import cd

from .bmi_setup import SetupMixIn
from .bmi_docstring import bmi_docstring
from .bmi_ugrid import (dataset_from_bmi_points,
                        dataset_from_bmi_uniform_rectilinear,
                        dataset_from_bmi_scalar)


class BmiError(Exception):
    def __init__(self, fname, status):
        self._fname = fname
        self._status = status

    def __str__(self):
        return 'Error calling BMI function: {fname} ({code})'.format(
            fname=self._fname, code=self._status)


def val_or_raise(func, args):
    rtn = func(*args)

    try:
        status, val = rtn
    except TypeError:
        status, val = rtn, None

    if status != 0:
        raise RuntimeError('%s(%s) [Error code %d]' % (
            func.__name__, ', '.join([repr(arg)for arg in args[1:]]), status))
    else:
        return val


def bmi_success_or_raise(bmi_status):
    try:
        status, val = bmi_status
    except TypeError:
        status, val = bmi_status, None

    if status != 0:
        raise RuntimeError('%s(%s) [Error code %d]' % (
            func.__name__, ', '.join([repr(arg)for arg in args[1:]]), status))
    else:
        return val


def bmi_call(func, *args):
    rtn = func(*args)

    try:
        status, val = rtn
    except TypeError:
        status, val = rtn, None

    if status != 0:
        raise BmiError(func.__name__ + pformat(args), status)
    else:
        return val


def wrap_set_value(func):
    def wrap(self, name, val):
        """Set a value by name.

        Parameters
        ----------
        name : str
            CSDMS standard name.
        val : array_like
            Values to set.
        """
        val = np.asarray(val).reshape((-1, ))
        return val_or_raise(func, (self._base, name, val))
    wrap.__name__ = func.__name__
    return wrap


def wrap_get_value(func):
    def wrap(self, name, out=None, units=None):
        """Get a value by name.

        Parameters
        ----------
        name : str
            CSDMS standard name.
        out : ndarray, optional
            Buffer to place values.
        units : str, optional
            Convert units of the returned values.

        Returns
        -------
        ndarray
            Array of values (or *out*, if provided).
        """
        if out is None:
            grid = self.get_var_grid(name)
            dtype = self.get_var_type(name)
            if dtype == '':
                print self.get_output_var_names()
                raise ValueError('{name} not understood'.format(name=name))
            out = np.empty(self.get_grid_size(grid), dtype=dtype)

        val_or_raise(func, (self._base, name, out))

        if units is not None:
            try:
                from_units = self.get_var_units(name)
            except AttributeError, NotImplementedError:
                pass
            else:
                Units.conform(out, Units(from_units), Units(units),
                              inplace=True)

        return out
    wrap.__name__ = func.__name__
    return wrap


def wrap_get_time(func):
    def wrap(self, units=None):
        time = val_or_raise(func, (self._base, ))
        if units is not None:
            try:
                from_units = Units(self.get_time_units())
                to_units = Units(units)
            except AttributeError, NotImplementedError:
                pass
            else:
                if not from_units.equals(to_units):
                    time = Units.conform(time, from_units, to_units)
        return time
    wrap.__name__ = func.__name__
    return wrap


def wrap_get_grid_with_out_arg(func, dtype):
    def wrap(self, grid, out=None):
        if out is None:
            out = np.empty(self.get_grid_rank(grid),
                           dtype=dtype)
        val_or_raise(func, (self._base, grid, out))
        return out
    wrap.__name__ = func.__name__
    return wrap


def wrap_var_names(func):
    def wrap(self):
        """Get input/output variable names.

        Returns
        -------
        tuple of str
            Variable names as CSDMS Standard Names.
        """
        return tuple(val_or_raise(func, (self._base, )))
    wrap.__name__ = func.__name__
    return wrap


def wrap_initialize(func):
    def wrap(self, *args, **kwds):
        if len(args) == 0:
            args = (self.setup(case=kwds.pop('case', 'default')), )
        val_or_raise(func, (self._base, ) + args)
    wrap.__name__ = func.__name__
    return wrap


def wrap_default(func):
    def wrap(self, *args):
        return val_or_raise(func, (self._base, ) + args)
    wrap.__name__ = func.__name__
    return wrap


def wrap_update_until(func):
    def wrap(self, then):
        if hasattr(self._base, 'update_until'):
            try:
                self._base.update_until(then)
            except NotImplementedError:
                pass

        while self.get_current_time() < then:
            self.update()

        if self.get_current_time() > then:
            pass


class TimeInterpolator(object):
    def __init__(self, method='linear'):
        self._method = method or 'linear'
        self._data = []
        self._time = []
        self._ti = None

        # self.add_data(data, time)

    def add_data(self, data, time):
        self._data.append(data)
        self._time.append(time)

        self._func = None

    def interpolate(self, time):
        if self._func is None:
            self._func = interp1d(self._time, self._data, axis=0,
                                  kind=self._method, fill_value='extrapolate')

        return self._func(time)


class BmiTimeInterpolator(object):
    # def __init__(self, method='linear'):
    def __init__(self, *args, **kwds):
        method = kwds.pop('method', 'linear')
        self._interpolators = dict(
            [(name, None) for name in self.output_var_names if '__' in name])
        self.reset(method=method)

        super(BmiTimeInterpolator, self).__init__(*args, **kwds)

    def reset(self, method='linear'):
        for name in self._interpolators:
            self._interpolators[name] = TimeInterpolator(method=method)

    def add_data(self):
        time = self.get_current_time()

        for name in self._interpolators:
            try:
                self._interpolators[name].add_data(self.get_value(name), time)
            except BmiError:
                self._interpolators.pop(name)
                print 'unable to get value for {name}. ignoring'.format(name=name)

    def interpolate(self, name, at):
        return self._interpolators[name].interpolate(at)

    def update_until(self, then, method=None, units=None):
        then = self.time_from(then, units)

        if hasattr(self.bmi, 'update_until'):
            try:
                bmi_call(self.bmi.update_until, then)
            except NotImplementedError:
                pass

        self.reset()
        while self.get_current_time() < then:
            if self.get_current_time() + self.get_time_step() > then:
                self.add_data()
            self.update()

        if self.get_current_time() > then:
            self.add_data()


def transform_math_to_azimuth(angle, units):
    angle *= -1.
    if units == Units('rad'):
        angle += np.pi * .5
    else:
        angle += 90.


def transform_azimuth_to_math(angle, units):
    angle *= -1.
    if units == Units('rad'):
        angle -= np.pi * .5
    else:
        angle -= 90.


class DataValues(object):
    def __init__(self, bmi, name):
        self._bmi = bmi
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def units(self):
        return self._bmi.get_var_units(self.name)

    @property
    def grid(self):
        return self._bmi.get_var_grid(self.name)

    @property
    def size(self):
        return self._bmi.get_var_size(self.name)

    @property
    def type(self):
        return self._bmi.get_var_type(self.name)

    @property
    def intent(self):
        return self._bmi.get_var_intent(self.name)

    @property
    def location(self):
        return self._bmi.get_var_location(self.name)

    @property
    def data(self):
        return self.values()

    def values(self, **kwds):
        if 'out' in self.intent:
            return self._bmi.get_value(self.name, **kwds)
        else:
            raise ValueError('not an output var')

    def __repr__(self):
        return str(self)

    def __str__(self):
        return """
<DataValues>
{dtype} {name}(n_nodes)
Attributes:
    units: {units}
    grid: {grid}
    intent: {intent}
    location: {location}
""".format(dtype=self.type, name=self.name, units=self.units,
           grid=self.grid, intent=self.intent, location=self.location).strip()


class _BmiCap(object):
    def __init__(self):
        self._bmi = self._cls()
        self._initialized = False
        self._grid = dict()
        self._var = dict()
        self._time_units = None
        super(_BmiCap, self).__init__()

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

    def _grid_ids(self):
        grids = set()
        for var in set(self.input_var_names + self.output_var_names):
            grids.add(self.get_var_grid(var))
        return tuple(grids)

    def get_component_name(self):
        return bmi_call(self.bmi.get_component_name)

    def initialize(self, fname=None, dir='.'):
        """Initialize the model.

        Parameters
        ----------
        fname : str
            Name of initialization file.
        dir : str
            Path to folder in which to run initialization.
        """
        # if len(args) == 0:
        #     args = (self.setup(case=kwds.pop('case', 'default')), )
        # if bmi_call(self.bmi.initialize, *args) == 0:
        #     self._initialized = True

        with cd(dir, create=False):
            if bmi_call(self.bmi.initialize, fname or '') == 0:
                self._initialized = True

        for grid_id in self._grid_ids():
            if self.get_grid_type(grid_id) == 'points':
                self._grid[grid_id] = dataset_from_bmi_points(self, grid_id)
            elif self.get_grid_type(grid_id) == 'uniform_rectilinear':
                self._grid[grid_id] = dataset_from_bmi_uniform_rectilinear(self, grid_id)
            elif self.get_grid_type(grid_id) == 'scalar':
                self._grid[grid_id] = dataset_from_bmi_scalar(self, grid_id)

        for name in set(self.output_var_names + self.input_var_names):
            self._var[name] = DataValues(self, name)

    def update(self):
        return bmi_call(self.bmi.update)

    def finalize(self):
        return bmi_call(self.bmi.finalize)

    def set_value(self, name, val):
        val = np.asarray(val).reshape((-1, ))
        return bmi_call(self.bmi.set_value, name, val)

    def get_value(self, name, out=None, units=None, angle=None, at=None,
                  method=None):
        if out is None:
            grid = self.get_var_grid(name)
            dtype = self.get_var_type(name)
            if dtype == '':
                raise ValueError('{name} not understood'.format(name=name))
            out = np.empty(self.get_grid_size(grid), dtype=dtype)

        bmi_call(self.bmi.get_value, name, out)

        if name in self._interpolators and at is not None:
            out[:] = self._interpolators[name].interpolate(at)

        from_units = Units(self.get_var_units(name))
        if units is not None:
            to_units = Units(units)
        else:
            to_units = from_units

        if units is not None and from_units != to_units:
            Units.conform(out, from_units, to_units, inplace=True)

        # if units is not None:
        #     try:
        #         from_units = self.get_var_units(name)
        #     except AttributeError, NotImplementedError:
        #         pass
        #     else:
        #         Units.conform(out, Units(from_units), Units(units),
        #                       inplace=True)

        if angle not in ('azimuth', 'math', None):
            raise ValueError('angle not understood')

        if angle == 'azimuth' and 'azimuth' not in name:
            transform_math_to_azimuth(out, to_units)
        elif angle == 'math' and 'azimuth' in name:
            transform_azimuth_to_math(out, to_units)

        return out

    def get_value_ptr(self, name):
        return bmi_call(self.bmi.get_value_ptr, name)

    def get_grid_rank(self, grid):
        return bmi_call(self.bmi.get_grid_rank, grid)

    def get_grid_size(self, grid):
        return bmi_call(self.bmi.get_grid_size, grid)

    def get_grid_type(self, grid):
        return bmi_call(self.bmi.get_grid_type, grid)

    def get_grid_shape(self, grid, out=None):
        if out is None:
            out = np.empty(self.get_grid_rank(grid), dtype='int32')
        bmi_call(self.bmi.get_grid_shape, grid, out)
        return out

    def get_grid_spacing(self, grid, out=None):
        if out is None:
            out = np.empty(self.get_grid_rank(grid), dtype=float)
        bmi_call(self.bmi.get_grid_spacing, grid, out)
        return out

    def get_grid_origin(self, grid, out=None):
        if out is None:
            out = np.empty(self.get_grid_rank(grid), dtype=float)
        bmi_call(self.bmi.get_grid_origin, grid, out)
        return out

    def get_grid_vertex_count(self, grid):
        return bmi_call(self.bmi.get_grid_vertex_count, grid)

    def get_grid_face_count(self, grid):
        return bmi_call(self.bmi.get_grid_face_count, grid)

    # def get_grid_connectivity(self, grid, out=None):
    def get_grid_face_node_connectivity(self, grid, out=None):
        if out is None:
            out = np.empty(self.get_grid_vertex_count(grid), dtype=np.int32)
        bmi_call(self.bmi.get_grid_connectivity, grid, out)
        return out

    # def get_grid_offset(self, grid, out=None):
    def get_grid_face_node_offset(self, grid, out=None):
        if out is None:
            out = np.empty(self.get_grid_face_count(grid), dtype=np.int32)
        bmi_call(self.bmi.get_grid_offset, grid, out)
        return out

    def get_grid_x(self, grid, out=None):
        if out is None:
            out = np.empty(self.get_grid_size(grid), dtype=float)
        bmi_call(self.bmi.get_grid_x, grid, out)
        return out

    def get_grid_y(self, grid, out=None):
        if out is None:
            out = np.empty(self.get_grid_size(grid), dtype=float)
        bmi_call(self.bmi.get_grid_y, grid, out)
        return out

    def get_grid_z(self, grid, out=None):
        if out is None:
            out = np.empty(self.get_grid_size(grid), dtype=float)
        bmi_call(self.bmi.get_grid_z, grid, out)
        return out

    @property
    def input_var_names(self):
        return tuple(bmi_call(self.bmi.get_input_var_names))

    def get_input_var_names(self):
        return self.input_var_names

    @property
    def output_var_names(self):
        return tuple(bmi_call(self.bmi.get_output_var_names))

    def get_output_var_names(self):
        return self.output_var_names

    @property
    def time_units(self):
        return self._time_units or self.get_time_units()
        # return self.get_time_units()

    @time_units.setter
    def time_units(self, new_units):
        self._time_units = new_units

    def get_time_units(self):
        return bmi_call(self.bmi.get_time_units)

    def get_current_time(self, units=None):
        time = bmi_call(self.bmi.get_current_time)

        return self.time_in(time, units)

    def get_start_time(self, units=None):
        time = bmi_call(self.bmi.get_start_time)

        return self.time_in(time, units)

    def get_end_time(self, units=None):
        time = bmi_call(self.bmi.get_end_time)

        return self.time_in(time, units)

    def get_time_step(self, units=None):
        time = bmi_call(self.bmi.get_time_step)

        return self.time_in(time, units)

    def time_in(self, time, units):
        if units is None:
            units = self.time_units
            # return time

        try:
            units_str = self.get_time_units()
            # units_str = self.time_units
        except (AttributeError, NotImplementedError):
            pass
        else:
            from_units = Units(units_str)
            to_units = Units(units)

            if not from_units.equals(to_units):
                time = Units.conform(time, from_units, to_units)

        return time

    def time_from(self, time, units):
        if units is None:
            return time

        try:
            # units_str = self.get_time_units()
            units_str = self.time_units
        except (AttributeError, NotImplementedError):
            pass
        else:
            to_units = Units(units_str)
            from_units = Units(units)

            if not from_units.equals(to_units):
                time = Units.conform(time, from_units, to_units)

        return time

    def get_var_intent(self, name):
        intent = ''
        if name in self.input_var_names:
            intent += 'in'
        if name in self.output_var_names:
            intent += 'out'
        return intent

    def get_var_location(self, name):
        return 'node'

    def get_var_grid(self, name):
        return bmi_call(self.bmi.get_var_grid, name)

    def get_var_itemsize(self, name):
        return bmi_call(self.bmi.get_var_itemsize, name)

    def get_var_nbytes(self, name):
        return bmi_call(self.bmi.get_var_nbytes, name)

    def get_var_type(self, name):
        return bmi_call(self.bmi.get_var_type, name)

    def get_var_units(self, name):
        units = bmi_call(self.bmi.get_var_units, name)
        if units == '-':
            return ''
        else:
            return units

    def as_dict(self):
        vars = {}
        grid_ids = set()
        for var in set(self.input_var_names + self.output_var_names):
            var_desc = {
                # 'name': var,
                'intent': '',
                'units': self.get_var_units(var),
                'dtype': self.get_var_type(var),
                'itemsize': self.get_var_itemsize(var),
                'nbytes': self.get_var_nbytes(var),
                'grid': self.get_var_grid(var),
            }
            vars[var] = var_desc

            if var in self.input_var_names:
                var_desc['intent'] += 'in'
            if var in self.output_var_names:
                var_desc['intent'] += 'out'
            # vars.append(var_desc)
            grid_ids.add(var_desc['grid'])
        # vars.sort(cmp=lambda a, b: cmp(a['name'], b['name']))

        grids = {}
        for grid_id in grid_ids:
            grid_desc = {
                # 'id': grid_id,
                'rank': self.get_grid_rank(grid_id),
                'size': self.get_grid_size(grid_id),
                'type': self.get_grid_type(grid_id),
            }
            grids[grid_id] = grid_desc
            # grids.append(grid_desc)
        # grids.sort(cmp=lambda a, b: cmp(a['id'], b['id']))

        in_vars = list(self.input_var_names)
        out_vars = list(self.output_var_names)
        in_vars.sort()
        out_vars.sort()

        times = {
            'start': self.get_start_time(),
            'end': self.get_end_time(),
            'current': self.get_current_time(),
            # 'time_step': self.get_time_step(),
            'units': self.get_time_units(),
        }
        return {
            'name': self.name,
            'input_var_names': in_vars,
            'output_var_names': out_vars,
            'vars': vars,
            'grids': grids,
            'times': times,
        }

    def as_yaml(self):
        return yaml.dump(self.as_dict(), default_flow_style=False)

    def as_json(self):
        return json.dumps(self.as_dict())

    def __str__(self):
        return yaml.dump({
            'name': self.name,
            'input_var_names': list(self.input_var_names),
            'output_var_names': list(self.output_var_names),
        }, default_flow_style=False)


class BmiCap(_BmiCap, BmiTimeInterpolator, SetupMixIn):
    pass


def bmi_factory(cls):
    class BmiWrapper(BmiCap):
        __doc__ = bmi_docstring(cls.__name__.split('.')[-1])
        _cls = cls

    BmiWrapper.__name__ = cls.__name__
    return BmiWrapper
