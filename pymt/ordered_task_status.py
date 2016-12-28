#! /usr/bin/env python
"""
>>> status = OrderedTaskStatus()
>>> status.start_task('create')
>>> print status
creating
>>> status.complete_task()
>>> print status
created

>>> status.start_task('initialize')
>>> print status
initializing
>>> status.start_task('initialize')
>>> print status
initializing

>>> status.complete_task()
>>> print status
initialized

"""

import types

from pymt.task_status import TaskStatus


class OrderedTaskStatus(object):
    """OrderedTaskStatus([task, [status]])

    >>> status = OrderedTaskStatus()
    >>> print status
    idling
    >>> print status.task
    create

    >>> status.start_task('create')
    >>> print status
    creating
    >>> status.complete_task()
    >>> print status
    created
    """
    def __init__(self, current=0, status='idling'):
        self._task_list = [
            TaskStatus('create', started='creating', completed='created'),
            TaskStatus('initialize', started='initializing',
                       completed='initialized'),
            TaskStatus('update', started='updating', completed='updated'),
            TaskStatus('finalize', started='finalizing', completed='finalized'),
        ]

        if isinstance(current, types.StringTypes):
            self._current = self.tasks.index(current)
        else:
            self._current = current
        self.current.update_to(status)

    def start_task(self, task, allow_restart=False):
        """
        Start *task* with the named string and set its status to the appropriate
        started string. If the previous task has not been completed, or if the
        *task* is already complete, raise ValueError.
        """
        if self._task_is_current(task):
            self.current.start(allow_restart=allow_restart)
        elif self._task_is_next(task):
            self._pop_next()
            self.current.start()
        else:
            raise ValueError('%s: task is not next' % task)

    def complete_task(self):
        """
        Complete the current task by setting its status to its completed string.
        """
        self.current.complete()

    @property
    def current(self):
        return self._task_list[self._current]

    @property
    def task(self):
        return self._task_list[self._current].name

    @property
    def status(self):
        return self._task_list[self._current].status

    @property
    def tasks(self):
        return [task.name for task in self._task_list]

    def _task_is_current(self, task):
        return task == self.current.name

    def _task_is_next(self, task):
        try:
            return self._task_list[self._current + 1].name == task
        except IndexError:
            return False

    def _pop_next(self):
        if self.current.is_completed():
            self._current += 1
        else:
            raise ValueError('current task is not complete')

    def __str__(self):
        return self.status

    def __repr__(self):
        kwds = ['current=%d' % self._current, 'status=%s' % repr(self.status)]
        return 'OrderedTaskStatus(%s)' % ', '.join(kwds)
