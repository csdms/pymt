from ConfigParser import ConfigParser
from StringIO import StringIO
import types

import yaml

from ..events.manager import EventManager
from ..events.port import PortEvent
from ..events.printer import PrintEvent

import services


class Component(object):
    def __init__(self, port, uses=set(), provides=set(), events=[]):
        if isinstance(port, types.StringTypes):
            self._port = services.get_port(port)
        else:
            self._port = port
        self._uses = uses
        self._provides = provides
        self._events = EventManager(
            [(self._port, self._port.time_step)] + events)

    @property
    def uses(self):
        return self._uses

    @property
    def provides(self):
        return self._provides

    def connect(self, uses, port):
        event = EventChain([port, MapEvent()])
        self._events.add_recurring_event(event, port._port.time_step)
        #self._events.add_recurring_event(port, port._port.time_step)

    def go(self):
        self.initialize()
        try:
            self.run(self._port.end_time)
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
    def from_path(cls, path, prefix='component'):
        with open(path, 'r') as yaml_file:
            return cls._from_yaml(yaml_file.read())

    @classmethod
    def _from_yaml(cls, contents):
        comp = yaml.load(contents)
        port = comp['name']

        events = []
        for conf in comp.get('print', []):
            conf['port'] = port
            events.append((PrintEvent(**conf), conf['interval']))

        uses = comp.get('uses', [])
        provides = comp.get('provides', [])

        return cls(port, uses=uses, provides=provides, events=events)
