"""Wrap a port as a :class:`Timeline` event.
"""

import os
import types

from ..mappers import NearestVal
from ..component.grid import GridMixIn
from ..utils.run_dir import open_run_dir
from ..framework import services


class PortEvent(GridMixIn):
    """Wrap a port as an event.

    Parameters
    ----------
    port : str
        Name of port.
    init_args : list, optional
        List of arguments to initialize port.
    run_dir : str, optional
        Path to directory to execute port.
    """
    def __init__(self, *args, **kwds):
        if isinstance(kwds['port'], types.StringTypes):
            self._port = services.get_component_instance(kwds['port'])
        else:
            self._port = kwds['port']

        self._init_args = kwds.get('init_args', [])
        self._run_dir = kwds.get('run_dir', '.')

        if isinstance(self._init_args, types.StringTypes):
            self._init_args = [self._init_args]
        self._status_fp = open(os.path.abspath(
            os.path.join(self._run_dir, '_time.txt')), 'w')
        GridMixIn.__init__(self)

    def initialize(self):
        """Initialize the event.

        Run the underlying port's initialization method in its *run_dir*. The event's *init_args* are passed to
        the initialize method as arguments.
        """
        with open_run_dir(self._run_dir):
            self._status_fp.write('%f' % 0.0)
            try:
                self._port.initialize(*self._init_args)
            except Exception:
                raise

    def run(self, time):
        """Run the event.

        Call the `run` method of the underlying port using *time* as the run time.

        Parameters
        ----------
        time : float
            Time to run the event to.
        """
        with open_run_dir(self._run_dir):
            self._status_fp.write('\n%f' % time)
            self._status_fp.flush()
            self._port.run(time)

    def update(self, time):
        with open_run_dir(self._run_dir):
            self._port.update(time)

    def finalize(self):
        """Finalize the event.

        Run the `finalize` method of the underlying port.
        """
        with open_run_dir(self._run_dir):
            self._status_fp.write('\ndone.')
            self._port.finalize()
        self._status_fp.close()


class PortMapEvent(object):
    """An event that maps values between ports.

    Parameters
    ----------
    src_port : str
        Port name that is the data source.
    dst_port : str
        Port name that is the destination.
    vars_to_map : list, optional
        Names of variable to map.
    method : {'direct', 'nearest'}, optional
        Method used to map values.
    """
    def __init__(self, *args, **kwds):
        if isinstance(kwds['src_port'], types.StringTypes):
            self._src = services.get_component_instance(kwds['src_port'])
        else:
            self._src = kwds['src_port']
        if isinstance(kwds['dst_port'], types.StringTypes):
            self._dst = services.get_component_instance(kwds['dst_port'])
        else:
            self._dst = kwds['dst_port']
        self._vars_to_map = kwds.get('vars_to_map', [])
        self._method = kwds.get('method', 'direct')

        if self._method == 'direct':
            self._mapper = None
        elif self._method == 'nearest':
            self._mapper = NearestVal()
        else:
            raise ValueError('method %s not understood' % self._method)

    def initialize(self):
        """Initialize the data mappers.
        """
        if self._mapper is not None:
            self._mapper.initialize(self._dst, self._src, vars=self._vars_to_map)

    def run(self, stop_time):
        """Map values from one port to another.
        """
        for (dst_name, src_name) in self._vars_to_map:
            src_values = self._src.get_value(src_name)

            if self._mapper is None:
                dst_values = src_values
            else:
                dst_values = self._mapper.run(src_values)

            self._dst.set_value(dst_name, dst_values)

    def finalize(self):
        pass
