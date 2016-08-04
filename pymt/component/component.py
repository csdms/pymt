"""
Examples
--------
Create an instance of the *AirPort* component and run it. The `go` method will initialize the component, run it for
its duration, and finalize it.

>>> from cmt.framework.services import register_component_classes
>>> register_component_classes(['cmt.testing.services.AirPort'])
>>> comp = Component('AirPort')
>>> comp.start_time
0.0
>>> comp.current_time
0.0
>>> comp.end_time
100.0
>>> comp.go()
>>> comp.current_time
100.0

If you try to create a new component with the same name, it will raise an exception. To create a new instance of the
component, you have to give it a new name.

>>> comp = Component('AirPort') # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
ValueError: AirPort
>>> comp = Component('AirPort', name='air_port')
>>> comp.current_time
0.0

You can gain finer control over component execution with the `initialize`, `run`, and `finalize` methods.

>>> comp.initialize()
>>> comp.run(10.)
>>> comp.current_time
10.0
>>> comp.run(101.) # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
ValueError: AirPort
>>> comp.current_time
10.0
>>> comp.run(100.)
>>> comp.current_time
100.0
>>> comp.finalize()
"""
import types
import warnings

import yaml

from ..events.manager import EventManager
from ..events.port import PortEvent, PortMapEvent
from ..events.printer import PrintEvent
from ..events.chain import ChainEvent
from .grid import GridMixIn

from ..framework import services


def clip_stop_time(stop, stop_min, stop_max):
    """Clip time between two values.

    Clip a stopping time between two values. This is the same as the numpy
    clip function except that if *stop* is `None` then *stop_max* is
    returned.

    Parameters
    ----------
    stop : float
        Stop time.
    stop_min : float
        Minimum stop time
    stop_max : float
        Maximum stop time

    Returns
    -------
    float
        The, possibly clipped, stop time.

    Examples
    --------
    >>> clip_stop_time(1., 0, 2.)
    1.0
    >>> clip_stop_time(1., 2, 3)
    2.0
    >>> clip_stop_time(4., 2, 3)
    3.0
    >>> clip_stop_time(None, 0, 1)
    1.0
    """
    from numpy import clip

    if stop is None:
        return float(stop_max)
    else:
        return clip(stop, stop_min, stop_max)


class Component(GridMixIn):
    """Wrap a BMI object as a component.

    Use the Component class to wrap an object that exposes a BMI so that it
    can operate within the model-coupling framework.

    Parameters
    ----------
    port : str or port-like
        Name of the port to wrap or a Port instance.
    uses : list, optional
        List of uses port names.
    provides : list, optional
        List of provides port names.
    argv : tuple, optional
        List of command line argument used to initialize the component.
    time_step : float, optional
        Time interval over which component will run uses ports.
    run_dir : str, optional
        Directory where the component will run.
    """
    def __init__(self, port, uses=None, provides=None, events=(), argv=(),
                 time_step=1., run_dir='.', name=None):
        if uses is None:
            uses = set()
        if provides is None:
            provides = set()

        if isinstance(port, types.StringTypes):
            if name is None:
                name = port
            self._port = services.instantiate_component(port, name)
        else:
            self._port = port
        self._uses = uses
        self._provides = provides
        self._time_step = time_step

        self._events = EventManager([
            (PortEvent(port=self._port, init_args=argv, run_dir=run_dir),
             time_step)
        ] + list(events))
        #self._events = EventManager([(self._port, 1.)] + events)
        #self._events = EventManager(
        #    [(self._port, self._port.time_step)] + events)

        GridMixIn.__init__(self)

    @property
    def time_step(self):
        """Component time step.

        Time step over which a component will update any connected uses ports.
        """
        return self._time_step

    @property
    def current_time(self):
        """Current time for component updating.
        """
        try:
            return self._port.current_time
        except AttributeError:
            return self._port.get_current_time()

    @property
    def start_time(self):
        """Start time for component updating.
        """
        try:
            return self._port.start_time
        except AttributeError:
            return self._port.get_start_time()

    @property
    def end_time(self):
        """End time for component updating.
        """
        try:
            return self._port.end_time
        except AttributeError:
            return self._port.get_end_time()

    @property
    def uses(self):
        """Names of connected *uses* ports.
        """
        return self._uses

    @property
    def provides(self):
        """Names of connected *provides* ports.
        """
        return self._provides

    def connect(self, uses, port, vars_to_map=()):
        """Connect a *uses* port to a *provides* port.

        Parameters
        ----------
        uses : str
            Name of the *uses* port.
        port : port-like
            Port-like object to connect to.
        var_to_map : iterable, optional
            Names of variables to map.
        """
        if uses not in self.uses:
            warnings.warn('component does not use %s' % uses)

        if len(vars_to_map) > 0:
            event = ChainEvent([port,
                                PortMapEvent(src_port=port, dst_port=self,
                                             vars_to_map=vars_to_map)])
            #PortMapEvent(src_port=port, dst_port=self._port,
        else:
            event = port
        self._events.add_recurring_event(event, port.time_step)
        #self._events.add_recurring_event(event, port._port.time_step)
        #self._events.add_recurring_event(port, port._port.time_step)

    def go(self, stop=None):
        """Run a component from start to end.

        Run a component starting from its start time and ending at its stop
        time. The component and any attached ports are first initialized,
        then updated until the end time and, finally, their finalize methods
        are called.

        Parameters
        ----------
        stop : float, optional
            Stop time, or None to run until `end_time`.
        """
        self.initialize()

        stop_time = clip_stop_time(stop, self.time_step, self.end_time)
        try:
            self.run(stop_time)
        except Exception:
            raise
        finally:
            self._events.finalize()

    def initialize(self):
        """Initialize a component and any connected events.
        """
        self._events.initialize()

    def run(self, stop_time):
        """Run a component and any connect events.

        Parameters
        ----------
        stop_time : float
            Time to run the component until.
        """
        if stop_time > self.end_time:
            raise ValueError('stop time is greater than end time.')
        self._events.run(stop_time)

    def finalize(self):
        """Finalize a component and any connected events.
        """
        self._events.finalize()

    def register(self, name):
        """Register component with the framework.

        Associate *name* with the component instance withing the framework.

        Parameters
        ----------
        name : str
            Name to associate component with.
        """
        services.register_component_instance(name, self)

    @classmethod
    def from_string(cls, source):
        """Deprecated.

        .. note:: Deprecated.
            Use :meth:`~Component.load` instead.

        Create a component from a string.

        Paramters
        ---------
        source : str
            Contents of a yaml file.

        Returns
        -------
        Component
            A newly-created component.
        """
        return cls._from_yaml(source)

    @classmethod
    def load(cls, source):
        """Create a Component from a string.

        This is an alternate constructor that create a component using values
        from a yaml-formatted string.

        Paramters
        ---------
        source : str
            Yaml-formatted string.

        Returns
        -------
        Component
            A newly-created component.
        """
        return cls.from_dict(yaml.load(source))

    @classmethod
    def load_all(cls, source):
        """Create multiple components from a string.

        This is an alternate constructor that creates a series of components
        using values from a yaml-formatted string.

        Paramters
        ---------
        source : str
            Yaml-formatted string.

        Returns
        -------
        List of Components
            A list of newly-created component.
        """
        components = []
        for section in yaml.load_all(source):
            components.append(cls.from_dict(section))
        return components

    @classmethod
    def from_dict(cls, d):
        """Create a Component instance from a dictionary.

        Use configuration paramters from a dict-like object to create a new
        Component. The dictionary must contain the following keys:
            - `name`
            - `class`
            - `initialize_args`
            - `time_step`
            - `run_dir`

        Parameters
        ----------
        d : dict-like
            Configuration parameters for the component.

        Returns
        -------
        Component
            A newly-created Component instance.
        """
        #port = services.get_port(d['name'])
        port = services.instantiate_component(d['class'], d['name'])
        #argv = d.get('argv', [])
        try:
            argv = d['initialize_args']
        except KeyError:
            argv = d.get('argv', [])
        time_step = float(d.get('time_step', 1.))
        run_dir = d.get('run_dir', '.')

        events = []
        for conf in d.get('print', []):
            conf['port'] = port
            conf['run_dir'] = run_dir
            events.append((PrintEvent(**conf), conf['interval']))

        uses = d.get('uses', [])
        provides = d.get('provides', [])

        return cls(port, uses=uses, provides=provides, events=events,
                   argv=argv, time_step=time_step, run_dir=run_dir)

    @classmethod
    def from_path(cls, path):
        """Create a component from a file.

        Parameters
        ----------
        path : str
            Path to yaml file.

        Returns
        -------
        Component
            A newly-created component.
        """
        with open(path, 'r') as yaml_file:
            return cls._from_yaml(yaml_file.read())

    @classmethod
    def _from_yaml(cls, contents):
        comp = yaml.load(contents)
        return cls.from_dict(comp)
