"""Wrap a port as a :class:`Timeline` event.
"""
import os
import sys

import six
import yaml

from ..component.grid import GridMixIn
from ..framework import services
from ..mappers import NearestVal
from ..utils import as_cwd


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
        if isinstance(kwds["port"], six.string_types):
            self._port = services.get_component_instance(kwds["port"])
        else:
            self._port = kwds["port"]

        self._init_args = kwds.get("init_args", [])
        self._run_dir = kwds.get("run_dir", ".")

        if isinstance(self._init_args, six.string_types):
            self._init_args = [self._init_args]

        self._status_fp = open(
            os.path.abspath(os.path.join(self._run_dir, "_time.txt")), "w"
        )

        GridMixIn.__init__(self)

    def initialize(self):
        """Initialize the event.

        Run the underlying port's initialization method in its *run_dir*. The event's *init_args* are passed to
        the initialize method as arguments.
        """
        with as_cwd(self._run_dir):
            status = {"name": self.name, "time": 0.0, "status": "initializing"}
            self._status_fp.write(yaml.dump(status))
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
        with as_cwd(self._run_dir):
            status = {"name": self.name, "time": time, "status": "running"}
            print(yaml.dump(status), file=self._status_fp)
            self._status_fp.flush()
            sys.stdout.flush()
            sys.stderr.flush()
            print(yaml.dump(status, default_flow_style=True))

            self._port.run(time)

            sys.stdout.flush()
            sys.stderr.flush()

    def update(self, time):
        with as_cwd(self._run_dir):
            self._port.update_until(time)

    def finalize(self):
        """Finalize the event.

        Run the `finalize` method of the underlying port.
        """
        with as_cwd(self._run_dir):
            status = {"name": self.name, "time": None, "status": "finishing"}
            self._status_fp.write(yaml.dump(status))
            self._port.finalize()
        status = {"name": self.name, "time": None, "status": "finished"}
        self._status_fp.write(yaml.dump(status))
        self._status_fp.close()


class PortMapEvent:
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
        if isinstance(kwds["src_port"], six.string_types):
            self._src = services.get_component_instance(kwds["src_port"])
        else:
            self._src = kwds["src_port"]
        if isinstance(kwds["dst_port"], six.string_types):
            self._dst = services.get_component_instance(kwds["dst_port"])
        else:
            self._dst = kwds["dst_port"]
        self._vars_to_map = kwds.get("vars_to_map", [])
        self._method = kwds.get("method", "direct")

        if self._method == "direct":
            self._mapper = None
        elif self._method == "nearest":
            self._mapper = NearestVal()
        else:
            raise ValueError("method %s not understood" % self._method)

    def initialize(self):
        """Initialize the data mappers."""
        if self._mapper is not None:
            self._mapper.initialize(self._dst, self._src, vars=self._vars_to_map)

    def run(self, stop_time):
        """Map values from one port to another."""
        for (dst_name, src_name) in self._vars_to_map:
            src_values = self._src.get_value(
                src_name, units=self._dst.get_var_units(dst_name)
            )

            if self._mapper is None:
                dst_values = src_values
            else:
                dst_values = self._mapper.run(src_values)

            self._dst.set_value(dst_name, dst_values)

    def finalize(self):
        pass
