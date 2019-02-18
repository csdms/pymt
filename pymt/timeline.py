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

>>> for event in timeline.iter_until(2.0): print(event)
event 2
event 2
event 2
event 1

>>> timeline.pop()
'event 2'

When events occur at the same time, events are popped in as first-in, first-out.

>>> timeline = Timeline([('event 1', 1.), ('event 2', .5)])
>>> for event in timeline.iter_until(1.0): print(event)
event 2
event 1
event 2

>>> timeline = Timeline([('event 2', .5), ('event 1', 1.)])
>>> timeline.pop_until(1.05)
['event 2', 'event 1', 'event 2']

>>> timeline.time
1.05

>>> for event in timeline.iter_until(1.05): print(event)
>>> timeline.time
1.05
>>> for event in timeline.iter_until(1.06): print(event)
>>> timeline.time
1.06

The event key can be any object, even a `tuple`.

>>> timeline = Timeline([(('event', 2), .5), (('event', 0), 1.)])
>>> for event in timeline.iter_until(1.05): print(event)
('event', 2)
('event', 0)
('event', 2)

Events do not have to be recurring.

>>> timeline = Timeline([(('event', 2), .5), (('event', 0), 1.)])
>>> timeline.add_one_time_event('one-timer', .1)
>>> for event in timeline.iter_until(1.05): print(event)
one-timer
('event', 2)
('event', 0)
('event', 2)
"""
import bisect


class Timeline(object):
    """Create a timeline of events.

    Parameters
    ----------
    events : dict-like
        Events as event-object/repeat interval pairs.
    start : float, optional
        Start time for the timeline.

    Examples
    --------
    Create a timeline with two recurring events. Events can be any old
    object. In this case they are two strings.

    >>> timeline = Timeline([('hello', 1.), ('world', 1.5)], start=3.)
    >>> sorted(timeline.events) # The events are returned as a set.
    ['hello', 'world']

    The first events will not occur at the starting time.

    >>> timeline.time
    3.0
    >>> timeline.next_event
    'hello'
    >>> timeline.time_of_next_event
    4.0

    To advance the timeline forward to the next event, use the `pop` method.

    >>> timeline.pop()
    'hello'
    >>> timeline.time
    4.0
    >>> timeline.pop()
    'world'
    >>> timeline.time
    4.5

    The timeline keeps track of objects, without making copies. The objects
    don't even need to be hashable.

    >>> hello = ['hello', 'world']
    >>> timeline = Timeline([(hello, 1.)])
    >>> event = timeline.pop()
    >>> event is hello
    True
    >>> event.append('!')
    >>> hello
    ['hello', 'world', '!']
    """

    def __init__(self, events=None, start=0.0):
        events = events or {}

        self._time = float(start)

        self._events = []
        self._times = []
        self._intervals = []

        self.add_recurring_events(events)

    @property
    def time(self):
        """Current time along the timeline.

        Examples
        --------
        >>> timeline = Timeline(start=0)
        >>> timeline.time
        0.0
        >>> timeline = Timeline(start=2)
        >>> timeline.time
        2.0
        """
        return self._time

    @property
    def next_event(self):
        """Next event object.

        Return the next event object but don't advance the timeline forward in
        time.

        Examples
        --------
        >>> timeline = Timeline([('an event', 1.)])
        >>> timeline.next_event
        'an event'
        >>> timeline.time
        0.0
        """
        try:
            return self._events[0]
        except IndexError:
            raise IndexError("empty timeline")

    @property
    def time_of_next_event(self):
        """Time when the next event will happen.

        Examples
        --------
        >>> timeline = Timeline([('an event', 1.)])
        >>> timeline.time_of_next_event
        1.0
        """
        try:
            return self._times[0]
        except IndexError:
            raise IndexError("empty timeline")

    @property
    def events(self):
        """All of the event objects in the timeline.

        Examples
        --------
        >>> timeline = Timeline([('an event', 1.), ('another event', 1.)])
        >>> events = timeline.events
        >>> isinstance(events, set)
        True
        >>> sorted(events)
        ['an event', 'another event']
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

        Examples
        --------
        >>> timeline = Timeline()
        >>> len(timeline.events)
        0
        >>> timeline.add_recurring_events([('hello', 1.), ('world', 1.)])
        >>> sorted(timeline.events)
        ['hello', 'world']

        Events pop as first-in, first-out.

        >>> timeline.pop()
        'hello'
        >>> timeline.pop()
        'world'

        The same event can be added multiple times.

        >>> timeline = Timeline()
        >>> timeline.add_recurring_events([('hello', 1.), ('world', 1.),
        ...     ('hello', 1.)])
        >>> sorted(timeline.events)
        ['hello', 'world']
        >>> timeline.pop_until(2.)
        ['hello', 'world', 'hello', 'hello', 'world', 'hello']
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

        Examples
        --------
        >>> timeline = Timeline()
        >>> timeline.add_recurring_event('say hello', 1.)
        >>> timeline.events == {'say hello'}
        True
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

        Examples
        --------
        >>> timeline = Timeline()
        >>> timeline.add_one_time_event('say hello', 1.)
        >>> timeline.time_of_next_event
        1.0
        >>> timeline.pop()
        'say hello'
        >>> timeline.time_of_next_event  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        IndexError: empty timeline
        """
        self._insert_event(event, time, None)

    def _insert_event(self, event, time, interval):
        index = bisect.bisect_right(self._times, time)

        self._times.insert(index, time)
        self._events.insert(index, event)
        self._intervals.insert(index, interval)

    def pop(self):
        """Pop the next event from the timeline.

        Examples
        --------
        >>> timeline = Timeline(dict(hello=1.))
        >>> timeline.pop()
        'hello'
        """
        try:
            (event, time, interval) = (
                self._events.pop(0),
                self._times.pop(0),
                self._intervals.pop(0),
            )
        except IndexError:
            raise IndexError("pop from empty timeline")

        try:
            self._insert_event(event, time + interval, interval)
        except TypeError:
            pass

        self._time = time

        return event

    def iter_until(self, stop):
        """Iterate the timeline until a given time.

        Iterate the timeline until *stop*, popping events along the way.

        Parameters
        ----------
        stop : float
            Time to iterate until.

        Returns
        -------
        event
            The next event object as the timeline advances to *stop*.
        """
        if stop < self.time:
            raise ValueError("stop time is less than current time")

        while self.time_of_next_event <= stop:
            yield self.pop()
        self._time = stop

    def pop_until(self, stop):
        """Advance the timeline, popping events along the way.

        Advance the timeline to *stop*, popping events along the way. Returns a
        list of the event objects that were popped to advance the timeline to
        *stop*.

        Parameters
        ----------
        stop : float
            Time to iterate until.

        Returns
        -------
        list
            The events popped to get to the stop time.

        Examples
        --------
        >>> timeline = Timeline([('a', 1.), ('b', 1.), ('c', 1.)])
        >>> timeline.pop_until(2.)
        ['a', 'b', 'c', 'a', 'b', 'c']
        """
        events = []
        for event in self.iter_until(stop):
            events.append(event)
        return events
