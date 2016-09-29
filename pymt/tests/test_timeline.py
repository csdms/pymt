#! /usr/bin/env python

import numpy as np
from nose.tools import (assert_equal, assert_set_equal, assert_raises,
                        assert_list_equal, assert_tuple_equal, assert_is)

from pymt.timeline import Timeline


def test_init_without_args():
    timeline = Timeline()
    assert_equal(0., timeline.time)
    assert_set_equal(set(), timeline.events)

    with assert_raises(IndexError):
        timeline.time_of_next_event
    with assert_raises(IndexError):
        timeline.next_event


def test_init_with_one_event():
    timeline = Timeline([('event 1', 1.)])

    assert_set_equal(set(['event 1']), timeline.events)
    assert_equal(1., timeline.time_of_next_event)
    assert_equal('event 1', timeline.next_event)


def test_init_with_two_events():
    timeline = Timeline([('event 1', 1.), ('event 2', .25)])

    assert_set_equal(set(['event 1', 'event 2']), timeline.events)
    assert_equal(.25, timeline.time_of_next_event)
    assert_equal('event 2', timeline.next_event)


def test_non_zero_start():
    timeline = Timeline([('event 1', 1.), ('event 2', .25)], start=-1)
    assert_equal(timeline.time_of_next_event, -.75)
    assert_list_equal(timeline.pop_until(0.),
                      ['event 2', 'event 2', 'event 2', 'event 1', 'event 2'])


def test_pop_empty_timeline():
    timeline = Timeline()
    with assert_raises(IndexError):
        timeline.pop()


def test_pop_events():
    timeline = Timeline([('event 1', 1.), ('event 2', .25)])
    for time in [.25, .5, .75]:
        assert_equal('event 2', timeline.pop())
        assert_equal(time, timeline.time)
    assert_equal('event 1', timeline.pop())
    assert_equal(1., timeline.time)

    assert_equal('event 2', timeline.pop())
    assert_equal(1., timeline.time)


def test_pop_until():
    timeline = Timeline([('event 1', 1.), ('event 2', .5)])
    events = timeline.pop_until(.2)
    assert_list_equal([], events)
    assert_equal(.2, timeline.time)

    events = timeline.pop_until(1.)
    assert_list_equal(['event 2', 'event 1', 'event 2'], events)
    assert_equal(1., timeline.time)


def test_hashable_event():
    timeline = Timeline([(('event', 2), .5), (('event', 0), 1.)])
    assert_tuple_equal(('event', 2), timeline.pop())
    assert_tuple_equal(('event', 0), timeline.pop())
    assert_tuple_equal(('event', 2), timeline.pop())


def test_unhashable_event():
    (first_event, second_event) = (dict(foo='bar'), dict(bar='baz'))
    timeline = Timeline([(first_event, .5), (second_event, 1.)])
    assert_is(first_event, timeline.pop())
    assert_is(second_event, timeline.pop())
    assert_is(first_event, timeline.pop())


def test_one_time_event():
    timeline = Timeline([('recurring-event', 1.), ])
    timeline.add_one_time_event('one-timer', .1)
    events = timeline.pop_until(2.)
    assert_list_equal(events,
                      ['one-timer', 'recurring-event', 'recurring-event'])


def test_repeated_events():
    (first_event, second_event) = (dict(foo='bar'), dict(bar='baz'))
    timeline = Timeline([(first_event, .5), (second_event, 1.),
                         (first_event, .75)])
    assert_is(first_event, timeline.pop())
    assert_is(first_event, timeline.pop())
    assert_is(second_event, timeline.pop())
    assert_is(first_event, timeline.pop())

    timeline = Timeline([(first_event, .5),
                         (second_event, 1.),
                         (first_event, 1.),
                        ])
    assert_is(first_event, timeline.pop())
    assert_is(second_event, timeline.pop())
    assert_is(first_event, timeline.pop())
    assert_is(first_event, timeline.pop())

    timeline = Timeline([(first_event, .5),
                         (first_event, 1.),
                         (second_event, 1.),
                        ])
    assert_is(first_event, timeline.pop())
    assert_is(first_event, timeline.pop())
    assert_is(second_event, timeline.pop())
    assert_is(first_event, timeline.pop())
