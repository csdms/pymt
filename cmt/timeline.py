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

The event key can be any object.

>>> timeline = Timeline([(('event', 2), .5), (('event', 0), 1.)])
>>> for event in timeline.iter_until(1.05): print event
('event', 2)
('event', 2)
('event', 0)

Events do not have to be recurring.

>>> timeline = Timeline([(('event', 2), .5), (('event', 0), 1.)])
>>> timeline.add_one_time_event('one-timer', .1)
>>> for event in timeline.iter_until(1.05): print event
one-timer
('event', 2)
('event', 2)
('event', 0)
"""
import sys
import bisect


class Timeline(object):
    def __init__(self, events={}, start=0.):
        self._time = start

        self._events = []
        self._times = []
        self._intervals = []

        self.add_recurring_events(events)

    @property
    def time(self):
        """Returns current time along the timeline.
        """
        return self._time

    @property
    def next_event(self):
        """Returns the next event object.
        """
        try:
            return self._events[0]
        except IndexError:
            raise IndexError('empty timeline')

    @property
    def time_of_next_event(self):
        """Return the time when the next event will happen.
        """
        try:
            return self._times[0]
        except IndexError:
            raise IndexError('empty timeline')

    @property
    def events(self):
        """Returns a set that contains all of the event objects.
        """
        return set(self._events)

    def add_recurring_events(self, events):
        """Adds recurring events to the timeline. *events* is a list where
        each element is tuple that gives the event object followed by the
        event recurrence interval.
        """
        try:
            event_items = events.items()
        except AttributeError:
            event_items = events

        for (event, interval) in event_items:
            self.add_recurring_event(event, interval)

    def add_recurring_event(self, event, interval):
        """Adds a single recurring event to the timeline. *event* is the
        event object, and *interval* is recurrence interval.
        """
        self._insert_event(event, self.time + interval, interval)

    def add_one_time_event(self, event, time):
        """Adds an event to the timeline that will only happen once.
        """
        self._insert_event(event, time, sys.float_info.max)

    def _insert_event(self, event, time, interval):
        index = bisect.bisect_left(self._times, time)

        self._times.insert(index, time)
        self._events.insert(index, event)
        self._intervals.insert(index, interval)

    def pop(self):
        """Pop the next event from the timeline.
        """
        try:
            (event, time, interval) = (self._events.pop(0),
                                       self._times.pop(0),
                                       self._intervals.pop(0))
        except IndexError:
            raise IndexError('pop from empty timeline')

        self._insert_event(event, time + interval, interval)

        self._time = time

        return event

    def iter_until(self, stop):
        """Iterate until *stop*, popping events along the way.

        Returns the next event object as the timeline advances to *stop*.
        """
        try:
            assert(stop >= self.time)
        except AssertionError:
            raise ValueError('stop time is less than current time')

        while self.time_of_next_event <= stop:
            yield self.pop()
        self._time = stop
        raise StopIteration

    def pop_until(self, stop):
        """Advance the timeline to *stop*, popping events along the way.

        Returns a list of the event objects that were popped to advance the
        timeline to *stop*.
        """
        events = []
        for event in self.iter_until(stop):
            events.append(event)
        return events
