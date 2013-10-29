#! /usr/bin/env python
"""
>>> timeline = Timeline()
>>> timeline.add_recurring_event('event 1', 1.)
>>> timeline.add_recurring_event('event 2', .3)
>>> timeline.pop()
'event 2'
>>> timeline.pop()
'event 2'
>>> timeline.pop()
'event 2'
>>> timeline.pop()
'event 1'

>>> timeline.time
1.0

>>> for event in timeline.iter_until(2.0): print event
event 2
event 2
event 2
event 1

>>> timeline.pop()
'event 2'

The order that events are added does not change the order they are popped
in the case when events happen at the same time. The most recent event goes
first.

>>> timeline = Timeline([('event 1', 1.), ('event 2', .5)])
>>> for event in timeline.iter_until(1.0): print event
event 2
event 2
event 1

>>> timeline = Timeline([('event 2', .5), ('event 1', 1.)])
>>> timeline.pop_until(1.05)
['event 2', 'event 2', 'event 1']

>>> timeline.time
1.05

>>> for event in timeline.iter_until(1.05): print event
>>> timeline.time
1.05
>>> for event in timeline.iter_until(1.06): print event
>>> timeline.time
1.06

The event key can be any hashable object.

>>> timeline = Timeline([(('event', 2), .5), (('event', 0), 1.)])
>>> for event in timeline.iter_until(1.05): print event
('event', 2)
('event', 2)
('event', 0)
"""

import bisect


class Timeline(object):
    def __init__(self, events={}):
        self._time = 0.
        self._event_times = []
        self._event_names = []
        self._event_intervals = dict()

        self.add_recurring_events(events)

    @property
    def time(self):
        return self._time

    @property
    def next_event(self):
        try:
            return self._event_names[0]
        except IndexError:
            raise IndexError('empty timeline')

    @property
    def time_of_next_event(self):
        try:
            return self._event_times[0]
        except IndexError:
            raise IndexError('empty timeline')

    @property
    def events(self):
        return set(self._event_intervals.keys())

    def add_recurring_events(self, events):
        try:
            event_items = events.items()
        except AttributeError:
            event_items = events

        for (name, interval) in event_items:
            self.add_recurring_event(name, interval)

    def add_recurring_event(self, name, interval):
        self._event_intervals[name] = interval
        self._insert_event(name, self.time + interval)

    def _insert_event(self, name, time):
        index = bisect.bisect_left(self._event_times, time)

        self._event_times.insert(index, time)
        self._event_names.insert(index, name)

    def pop(self):
        try:
            name = self._event_names.pop(0)
            time = self._event_times.pop(0)
        except IndexError:
            raise IndexError('pop from empty timeline')

        self._insert_event(name, time + self._event_intervals[name])

        self._time = time

        return name

    def iter_until(self, stop):
        try:
            assert(stop >= stop)
        except AssertionError:
            raise ValueError('stop time is less than current time')

        while self.time_of_next_event <= stop:
            yield self.pop()
        self._time = stop
        raise StopIteration

    def pop_until(self, stop):
        events = []
        for event in self.iter_until(stop):
            events.append(event)
        return events
