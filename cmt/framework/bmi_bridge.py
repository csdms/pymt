import numpy as np
from .bmi_setup import SetupMixIn
from .bmi_docstring import bmi_docstring


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
    def wrap(self, name, out=None):
        """Get a value by name.

        Parameters
        ----------
        name : str
            CSDMS standard name.
        out : ndarray, optional
            Buffer to place values.

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
        return out
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


def bmi_factory(cls):
    import inspect

    class BmiWrapper(SetupMixIn):
        __doc__ = bmi_docstring(cls.__name__.split('.')[-1])
        _cls = cls
        def __init__(self):
            self._base = self._cls()
            super(BmiWrapper, self).__init__()

    for name, func in inspect.getmembers(cls):
        if name == 'initialize':
            setattr(BmiWrapper, name, wrap_initialize(func))
        elif name == 'set_value':
            setattr(BmiWrapper, name, wrap_set_value(func))
        elif name == 'get_value':
            setattr(BmiWrapper, name, wrap_get_value(func))
        elif name in ('get_grid_spacing', 'get_grid_origin'):
            setattr(BmiWrapper, name, wrap_get_grid_with_out_arg(func, float))
        elif name == 'get_grid_shape':
            setattr(BmiWrapper, name, wrap_get_grid_with_out_arg(func, 'int32'))
        elif name in ('get_input_var_names', 'get_output_var_names'):
            setattr(BmiWrapper, name, wrap_var_names(func))
        elif name.startswith('get_') or name in ('update', 'update_until', 'finalize'):
            setattr(BmiWrapper, name, wrap_default(func))
        else:
            pass
    BmiWrapper.__name__ = cls.__name__
    return BmiWrapper
