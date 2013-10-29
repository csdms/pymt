#! /usr/bin/env python

import unittest

from cmt.ordered_task_status import OrderedTaskStatus


class TestOrderedTaskStatus(unittest.TestCase):
    def test_init(self):
        queue = OrderedTaskStatus()
        self.assertEqual('create', queue.task)
        self.assertEqual('idling', queue.status)
        self.assertListEqual(['create', 'initialize', 'update', 'finalize'],
                             queue.tasks)

    def test_start_task(self):
        queue = OrderedTaskStatus()
        queue.start_task('create')
        self.assertEqual('create', queue.task)
        self.assertEqual('creating', queue.status)

    def test_start_completed_task(self):
        queue = OrderedTaskStatus()
        queue.start_task('create')
        queue.complete_task()

        with self.assertRaises(ValueError):
            queue.start_task('create')

    def test_restart_completed_task(self):
        queue = OrderedTaskStatus()
        queue.start_task('create')
        queue.complete_task()

        queue.start_task('create', allow_restart=True)
        self.assertEqual('create', queue.task)
        self.assertEqual('creating', queue.status)

    def test_restart_previous_task(self):
        queue = OrderedTaskStatus()
        queue.start_task('create')
        queue.complete_task()

        queue.start_task('initialize')
        queue.complete_task()

        with self.assertRaises(ValueError):
            queue.start_task('create', allow_restart=True)

    def test_start_next_before_finish_current(self):
        queue = OrderedTaskStatus()
        queue.start_task('create')
        with self.assertRaises(ValueError):
            queue.start_task('initialize')

    def test_complete_task(self):
        queue = OrderedTaskStatus()
        queue.start_task('create')
        queue.complete_task()
        self.assertEqual('create', queue.task)
        self.assertEqual('created', queue.status)

    def test_complete_before_started(self):
        queue = OrderedTaskStatus()
        with self.assertRaises(ValueError):
            queue.complete_task()

    def test_all_tasks(self):
        queue = OrderedTaskStatus()
        for task in queue.tasks:
            queue.start_task(task)
            queue.complete_task()

    def test_skip_task(self):
        queue = OrderedTaskStatus()
        queue.start_task('create')
        queue.complete_task()
        
        tasks = queue.tasks
        for task in tasks[2:]:
            with self.assertRaises(ValueError):
                queue.start_task(task)

    def test_move_backward(self):
        queue = OrderedTaskStatus()
        for task in queue.tasks:
            queue.start_task(task)
            queue.complete_task()
        
        tasks = queue.tasks
        for task in tasks[:-1]:
            with self.assertRaises(ValueError):
                queue.start_task(task)
