"""Manage the execution of events on a timeline.

The :class:`EventManager` puts events on a :class:`~cmt.timeline.Timeline` and
then
orchestrates the setup, execution, and teardown of the events as the time line
advances. Events are classes that implement an event interface. That is, they
implement the following methods:

* `initialize()`
* `run(time)`
* `finalize()`

Because the :class:`EventManager` class itself is event-like, it is able to
manage other :class:`EventManager` instances and even handle recursive events.

Examples
--------
Create an event that prints, "hello".

>>> class PrintHello(object):
...     def initialize(self):
...         print "hello from initialize"
...     def run(self, time):
...         print "hello!"
...     def finalize(self):
...         print "hello from finalize"

Add an instance of the event to be run at a regular interval to the manager.

>>> mngr = EventManager([(PrintHello(), 2.)])
>>> mngr.initialize()
hello from initialize
>>> mngr.run(1.)
>>> mngr.run(2.)
hello!
>>> mngr.finalize()
hello from finalize

You can also use an :class:`EventManager` as a context,

>>> with EventManager([(PrintHello(), 2.)]) as mngr:
...     mngr.run(4.)
hello from initialize
hello!
hello!
hello from finalize
"""

from ..timeline import Timeline
from ..utils.prefix import names_with_prefix, strip_prefix


class EventManager(object):
    """
    Parameters
    ----------
    events : dict-like
        Events as event-object/repeat interval pairs.

    See Also
    --------
    :class:`cmt.timeline.Timeline`

    Examples
    --------
    Create an :class:`EventManager` without any events.

    >>> mngr = EventManager()
    >>> mngr.time
    0.0
    >>> len(mngr)
    0

    Create a manager with one recurring event.

    >>> from cmt.events.empty import PassEvent
    >>> mngr = EventManager([(PassEvent(), 1.)])
    >>> len(mngr)
    1

    Create a manager with two recurring events.

    >>> mngr = EventManager([(PassEvent(), 1.), (PassEvent(), 2.)])
    >>> len(mngr)
    2
    """
    def __init__(self, *args):
        if len(args) > 1:
            raise TypeError("__init__() takes 1 or 2 arguments (%d given)" %
                            (len(args) + 1, ))

        self._timeline = Timeline(*args)
        self._initializing = False
        self._initialized = False
        self._running = False
        self._finalizing = False

        self._order = list(*args)

    def initialize(self):
        """Initialize the managed events.

        Execute the `initialize` methods of each of the events that are being
        managed, making sure the manager is not initialized if it is already
        in the initialization process. Events are initialized in the order
        they were given at creation.
        """
        if not self._initializing:
            self._initializing = True
            for (event, _) in self._order:
                try:
                    event.initialize()
                except Exception:
                    print 'error initializing'
                    print event
                    raise
            self._initialized = True

    def run(self, stop_time):
        """Run events until some time.

        Execute the `run` method of each of the events being managed until
        *stop_time* is reached on the time line.

        Parameters
        ----------
        stop_time : float
            Time to run events until.
        """
        self.initialize()
        if not self._running:
            self._running = True
            for event in self._timeline.iter_until(stop_time):
                try:
                    event.run(self._timeline.time)
                except AttributeError:
                    event.update(self._timeline.time)
            self._running = False

    def finalize(self):
        """Finalize managed events.

        Execute the `finalize` method for each of the events being managed.
        Events are finalized in the reverse order in which they were
        initialized, and only if the manager has not yet been initialized.
        """
        if self._initialized:
            if not self._finalizing:
                self._finalizing = True
                #for event in self._timeline.events:
                for (event, _) in self._order[::-1]:
                    event.finalize()
            self._initialized = False

    def add_recurring_event(self, event, interval):
        """Add a managed event.

        Add *event* to the list of managed events and run it with the
        recurrence interval, *interval*.

        Parameters
        ----------
        event : event-like
            Event to be managed.
        interval : float
            Recurrence interval for the event.
        """
        self._timeline.add_recurring_event(event, interval)
        self._order.append((event, interval))

    @property
    def time(self):
        """Current time along the time line.
        """
        return self._timeline.time

    @classmethod
    def from_string(cls, source, prefix=''):
        """Create an `EventManager` from a string.

        Parameters
        ----------
        source : str
            Ini-formatted string.
        prefix : str
            Prefix for section.

        Returns
        -------
        EventManager
            A newly-created `EventManager`.

        See Also
        --------
        :method:`from_path` : Alternate constructor that uses a path name.
        """
        config = ConfigParser()
        config.readfp(StringIO(source))
        return cls._from_config(config, prefix=prefix)

    @classmethod
    def from_path(cls, path, prefix=''):
        """Create an `EventManager` from a file.

        Parameters
        ----------
        path : str
            Path to ini-formatted file.
        prefix : str
            Prefix for section.

        Returns
        -------
        EventManager
            A newly-created `EventManager`.

        See Also
        --------
        :method:`from_string` : Alternate constructor that uses a string.
        """
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

    def __len__(self):
        return len(self._order)
