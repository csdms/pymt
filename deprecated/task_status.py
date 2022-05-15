#! /bin/env python

from collections import OrderedDict

_TASK_STATUS_STRINGS = OrderedDict(
    [
        ("create", ("creating", "created")),
        ("initialize", ("initializing", "initialized")),
        ("update", ("updating", "updated")),
        ("finalize", ("finalizing", "finalized")),
    ]
)
_TASK_NAMES_IN_ORDER = _TASK_STATUS_STRINGS.keys()
_TASK_COUNT = len(_TASK_NAMES_IN_ORDER)
_TASK_NAME_TO_ID = dict(zip(_TASK_NAMES_IN_ORDER, range(_TASK_COUNT)))

_FIRST_TASK_ID = 0
_LAST_TASK_ID = _TASK_COUNT - 1

TASK_STARTED = 0
TASK_COMPLETED = 1
IDLE = -1


def task_id_as_string(task):
    try:
        return _TASK_NAMES_IN_ORDER[task]
    except IndexError:
        raise ValueError(task)


def task_status_as_string(task, status):
    if status == IDLE:
        return "idling"
    else:
        return _TASK_STATUS_STRINGS[task_id_as_string(task)][status]


def task_string_as_integer(task):
    try:
        return _TASK_NAME_TO_ID[task]
    except KeyError:
        raise ValueError(task)


def task_as_valid_integer(task):
    if task >= _FIRST_TASK_ID and task <= _LAST_TASK_ID:
        return task
    else:
        raise ValueError(task)


def task_as_integer(task):
    if isinstance(task, str):
        return task_string_as_integer(task)
    else:
        return task_as_valid_integer(task)


class TaskStatus:
    def __init__(
        self,
        name,
        started="started",
        completed="completed",
        idling="idling",
        status="idling",
    ):
        self._name = name
        self._status_strings = {
            "started": started,
            "completed": completed,
            "idling": idling,
        }
        self._status = getattr(self, self._normalize_status_string(status))

    @property
    def name(self):
        return self._name

    @property
    def status(self):
        return self._status

    @property
    def started(self):
        return self._status_strings["started"]

    @property
    def completed(self):
        return self._status_strings["completed"]

    @property
    def idling(self):
        return self._status_strings["idling"]

    def start(self, allow_restart=False):
        if not allow_restart and self.is_completed():
            raise ValueError("%s: Task has already completed" % self.name)
        self._status = self.started

    def complete(self):
        if self.is_started() or self.is_completed():
            self._status = self.completed
        else:
            raise ValueError("%s: Task not started" % self.name)

    def idle(self):
        if self.is_started():
            raise ValueError("%s: Task already started" % self.name)
        elif self.is_completed():
            raise ValueError("%s: Task already completed" % self.name)
        else:
            self._status = self.idling

    def update_to(self, status):
        status = self._normalize_status_string(status)
        if status == "idling":
            self.idle()
        elif status == "started":
            self.start()
        elif status == "completed":
            self.start()
            self.complete()
        else:
            raise ValueError(status)

    def is_started(self):
        return self._status == self.started

    def is_completed(self):
        return self._status == self.completed

    def _normalize_status_string(self, status):
        if status in self._status_strings:
            return status
        else:
            for (norm_status, value) in self._status_strings.items():
                if status == value:
                    return norm_status

    def __str__(self):
        return "%s: %s" % (self.name, self.status)

    def __repr__(self):
        kwds = []
        for (key, value) in self._status_strings.items():
            kwds.append("%s=%s" % (key, repr(value)))
        kwds.append("status=%s" % repr(self._status))
        return "TaskStatus(%s, %s)" % (repr(self.name), ", ".join(kwds))


if __name__ == "__main__":
    import doctest

    doctest.testmod()
