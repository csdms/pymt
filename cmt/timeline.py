#! /usr/bin/env python
"""Execute events along a timeline.

Examples
--------
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
    """Create a timeline of events.
    Parameters
    ----------
    events : dict-like
        Events as event-object/repeat interval pairs.
    start : float, optional
        Start time for the timeline.
    """
    def __init__(self, events={}, start=0.):
        self._time = start

        self._events = []
        self._times = []
        self._intervals = []

        self.add_recurring_events(events)

    @property
    def time(self):
        """Current time along the timeline.
        """
        return self._time

    @property
    def next_event(self):
        """Next event object.
        """
        try:
            return self._events[0]
        except IndexError:
            raise IndexError('empty timeline')

    @property
    def time_of_next_event(self):
        """Time when the next event will happen.
        """
        try:
            return self._times[0]
        except IndexError:
            raise IndexError('empty timeline')

    @property
    def events(self):
        """All of the event objects in the timeline.
        """
        return set(self._events)

    def add_recurring_events(self, events):
        """Add a series of recurring events to the timeline.
        
        Adds recurring events to the timeline. *events* is a list where
        each element is tuple that gives the event object followed by the
        event recurrence interval.

        Parameters
        ----------
        events : dict-like
            Events object/interval pairs to add to the timeline.
        """
        try:
            event_items = events.items()
        except AttributeError:
            event_items = events

        for (event, interval) in event_items:
            self.add_recurring_event(event, interval)

    def add_recurring_event(self, event, interval):
        """Add a recurring event to the timeline.

        Adds a single recurring event to the timeline. *event* is the
        event object, and *interval* is recurrence interval.

        Parameters
        ----------
        event : event-like
            Event to add to the timeline.
        interval : float
            Recurrence interval of the event.
        """
        self._insert_event(event, self.time + interval, interval)

    def add_one_time_event(self, event, time):
        """Add an event that will only happen once.

        Parameters
        ----------
        event : event-like
            Event to add to the timeline.
        time : float
            Time for the event to execute.
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
        """Iterate the timeline until a given time.

        Iterate the timeline until *stop*, popping events along the way.

        Paramters
        ---------
        stop : float
            Time to iterate until.

        Returns
        -------
        event
            The next event object as the timeline advances to *stop*.
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
        """Advance the timeline, popping events along the way.

        Advance the timeline to *stop*, popping events along the way. Returns a
        list of the event objects that were popped to advance the timeline to
        *stop*.

        Paramters
        ---------
        stop : float
            Time to iterate until.

        Returns
        -------
        list
            The events popped to get to the stop time.
        """
        events = []
        for event in self.iter_until(stop):
            events.append(event)
        return events
