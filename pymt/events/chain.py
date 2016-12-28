
class ChainEvent(object):
    def __init__(self, events):
        self._events = events

    def initialize(self):
        for event in self._events:
            event.initialize()

    def run(self, stop_time):
        for event in self._events:
            event.run(stop_time)

    def update(self, stop_time):
        for event in self._events:
            event.run(stop_time)

    def finalize(self):
        for event in self._events:
            event.finalize()
