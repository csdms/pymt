"""An empty event.

:class:`PassEvent` implements an event-like interface but doesn't do
anything. This can be a useful event to give to an :class:`EventManager` if
you want to force the manager to stop at particular intervals.
"""


class PassEvent(object):
    """An event that doesn't do anything.
    """
    def initialize(self):
        pass

    def run(self, stop_time):
        pass

    def finalize(self, stop_time):
        pass
