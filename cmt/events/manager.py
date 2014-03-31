from ..timeline import Timeline
from ..utils.prefix import names_with_prefix, strip_prefix


class EventManager(object):
    def __init__(self, events):
        self._timeline = Timeline(events)

    def initialize(self):
        for event in self._timeline.events:
            event.initialize()

    def run(self, stop_time):
        for event in self._timeline.iter_until(stop_time):
            event.run(self._timeline.time)

    def finalize(self):
        for event in self._timeline.events:
            event.finalize()

    @property
    def time(self):
        return self._timeline.time

    @classmethod
    def from_string(cls, source, prefix=''):
        config = ConfigParser()
        config.readfp(StringIO(source))
        return cls._from_config(config, prefix=prefix)

    @classmethod
    def from_path(cls, path, prefix=''):
        config = ConfigParser()
        config.read(path)
        return cls._from_config(config, prefix=prefix)

    @classmethod
    def _from_config(cls, config, prefix=''):
        event_names = names_with_prefix(config.sections(), prefix)
        events = []
        for name in event_names:
            events.append((name, config.get(name, 'interval')))
        return cls(events)

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, type, value, traceback):
        self.finalize()
