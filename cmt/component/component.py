from ConfigParser import ConfigParser
from StringIO import StringIO
import types

import yaml

from ..events.manager import EventManager
from ..events.port import PortEvent, PortMapEvent
from ..events.printer import PrintEvent
from ..events.chain import ChainEvent
from .grid import GridMixIn

#import services
from ..framework import services

def clip_stop_time(stop, stop_min, stop_max):
    from numpy import clip

    if stop is None:
        return stop_max
    else:
        return clip(stop, stop_min, stop_max)


class Component(GridMixIn):
    def __init__(self, port, uses=set(), provides=set(), events=[], argv=[],
                time_step=1., run_dir='.'):
        if isinstance(port, types.StringTypes):
            self._port = services.get_port(port)
        else:
            self._port = port
        self._uses = uses
        self._provides = provides
        self._time_step = time_step

        self._events = EventManager([
            (PortEvent(port=self._port, init_args=argv, run_dir=run_dir),
             time_step)
        ] + events)
        #self._events = EventManager([(self._port, 1.)] + events)
        #self._events = EventManager(
        #    [(self._port, self._port.time_step)] + events)

        GridMixIn.__init__(self)

    @property
    def time_step(self):
        return self._time_step

    @property
    def end_time(self):
        try:
            return self._port.end_time
        except AttributeError:
            return self._port.get_end_time()

    @property
    def uses(self):
        return self._uses

    @property
    def provides(self):
        return self._provides

    def connect(self, uses, port, vars_to_map=[]):
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
        print 'go!'
        self.initialize()

        stop_time = clip_stop_time(stop, self.time_step, self.end_time)
        try:
            self.run(stop_time)
        except Exception:
            raise
        finally:
            self._events.finalize()

    def initialize(self):
        self._events.initialize()

    def run(self, stop_time):
        self._events.run(stop_time)

    def finalize(self):
        self._events.finalize()

    def register(self, name):
        services.register_component(self, name)

    @classmethod
    def from_string(cls, source):
        return cls._from_yaml(source)

    @classmethod
    def load(cls, source):
        return cls.from_dict(yaml.load(source))

    @classmethod
    def load_all(cls, source):
        components = []
        for section in yaml.load_all(source):
            components.append(cls.from_dict(section))
        return components

    @classmethod
    def from_dict(cls, d):
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
    def from_path(cls, path, prefix='component'):
        with open(path, 'r') as yaml_file:
            return cls._from_yaml(yaml_file.read())

    @classmethod
    def _from_yaml(cls, contents):
        comp = yaml.load(contents)
        return cls.from_dict(comp)
