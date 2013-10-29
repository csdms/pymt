#! /usr/bin/env python

import unittest
import numpy as np

from cmt.timeline import Timeline


class TestTimeline(unittest.TestCase):
    def test_init_without_args(self):
        timeline = Timeline()
        self.assertEqual(0., timeline.time)
        self.assertSetEqual(set(), timeline.events)

        with self.assertRaises(IndexError):
            timeline.time_of_next_event
        with self.assertRaises(IndexError):
            timeline.next_event

    def test_init_with_one_event(self):
        timeline = Timeline([('event 1', 1.)])

        self.assertSetEqual(set(['event 1']), timeline.events)
        self.assertEqual(1., timeline.time_of_next_event)
        self.assertEqual('event 1', timeline.next_event)

    def test_init_with_two_events(self):
        timeline = Timeline([('event 1', 1.), ('event 2', .25)])

        self.assertSetEqual(set(['event 1', 'event 2']), timeline.events)
        self.assertEqual(.25, timeline.time_of_next_event)
        self.assertEqual('event 2', timeline.next_event)

    def test_pop_empty_timeline(self):
        timeline = Timeline()
        with self.assertRaises(IndexError):
            timeline.pop()

    def test_pop_events(self):
        timeline = Timeline([('event 1', 1.), ('event 2', .25)])
        for time in [.25, .5, .75, 1.]:
            self.assertEqual('event 2', timeline.pop())
            self.assertEqual(time, timeline.time)
        self.assertEqual('event 1', timeline.pop())
        self.assertEqual(1., timeline.time)

    def test_pop_until(self):
        timeline = Timeline([('event 1', 1.), ('event 2', .5)])
        events = timeline.pop_until(.2)
        self.assertListEqual([], events)
        self.assertEqual(.2, timeline.time)

        events = timeline.pop_until(1.)
        self.assertListEqual(['event 2', 'event 2', 'event 1'], events)
        self.assertEqual(1., timeline.time)

    def test_hashable_name(self):
        timeline = Timeline([(('event', 2), .5), (('event', 0), 1.)])
        self.assertTupleEqual(('event', 2), timeline.pop())
        self.assertTupleEqual(('event', 2), timeline.pop())
        self.assertTupleEqual(('event', 0), timeline.pop())
