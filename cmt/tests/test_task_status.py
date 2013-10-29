#! /usr/bin/env python

import unittest

from cmt.task_status import TaskStatus


class TestTaskStatus(unittest.TestCase):
    def test_init(self):
        task = TaskStatus('task name')
        self.assertEqual(task.name, 'task name')
        self.assertEqual(task.status, task.idling)

    def test_init_with_kwds(self):
        task = TaskStatus('initialize', started='initializing',
                          completed='initialized')

        self.assertEqual(task.name, 'initialize')
        self.assertEqual(task.idling, 'idling')
        self.assertEqual(task.started, 'initializing')
        self.assertEqual(task.completed, 'initialized')

    def test_start(self):
        task = TaskStatus('task name')
        self.assertEqual(task.status, task.idling)

        task.start()
        self.assertEqual(task.status, task.started)

    def test_complete(self):
        task = TaskStatus('task name')
        task.start()
        task.complete()
        self.assertEqual(task.status, task.completed)

    def test_start_already_started(self):
        task = TaskStatus('task')

        for _ in xrange(10):
            task.start()
            self.assertEqual(task.status, task.started)

    def test_start_already_completed(self):
        task = TaskStatus('task')

        task.start()
        task.complete()
        with self.assertRaises(ValueError):
            task.start()

        task.start(allow_restart=True)
        self.assertTrue(task.is_started())

    def test_complete_unstarted(self):
        task = TaskStatus('task name')
        with self.assertRaises(ValueError):
            task.complete()

    def test_complete_already_completed(self):
        task = TaskStatus('task name')
        task.start()
        task.complete()
        task.complete()

    def test_update_to(self):
        task = TaskStatus('task')
        task.update_to('completed')
        self.assertEqual(task.completed, task.status)
        self.assertTrue(task.is_completed())

    def test_is_started(self):
        task = TaskStatus('task')
        self.assertFalse(task.is_started())

        task.start()
        self.assertTrue(task.is_started())

        task.complete()
        self.assertFalse(task.is_started())

    def test_is_completed(self):
        task = TaskStatus('task')
        self.assertFalse(task.is_completed())

        task.start()
        self.assertFalse(task.is_completed())

        task.complete()
        self.assertTrue(task.is_completed())

    def test_str(self):
        task = TaskStatus('my_task')
        self.assertEqual(str(task), 'my_task: idling')

        task.start()
        self.assertEqual(str(task), 'my_task: started')

        task.complete()
        self.assertEqual(str(task), 'my_task: completed')

        task = TaskStatus('my_task', started='creating', completed='created')
        self.assertEqual(str(task), 'my_task: idling')

        task.start()
        self.assertEqual(str(task), 'my_task: creating')

        task.complete()
        self.assertEqual(str(task), 'my_task: created')
