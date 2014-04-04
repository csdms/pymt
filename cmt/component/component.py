from ConfigParser import ConfigParser
from StringIO import StringIO

from ..events.manager import EventManager


class Component(object):
    def __init__(self, port):
        if isinstance(port, types.StringTypes):
            self._port = services.get_port(port)
        else:
            self._port = port
        self._events = EventManager()

    def go(self):
        self._events.run(self._port.end_time)

    def register(self):
        pass

    @classmethod
    def from_string(cls, source, prefix='component'):
        config = ConfigParser()
        config.readfp(StringIO(source))
        return cls._from_config(config, prefix=prefix)

    @classmethod
    def from_path(cls, path, prefix='component'):
        config = ConfigParser()
        config.read(path)
        return cls._from_config(config, prefix=prefix)

    @classmethod
    def _from_config(cls, config, prefix='component'):
        component_names = names_with_prefix(config.sections(), prefix)
        events = []
        for name in event_names:
            events.append((name, config.get(name, 'interval')))
        return cls(events)

