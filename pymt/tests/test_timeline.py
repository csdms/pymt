#! /usr/bin/env python
import pytest
from pytest import approx

from pymt.timeline import Timeline


def test_init_without_args():
    timeline = Timeline()
    assert 0. == timeline.time
    assert set() == timeline.events

    with pytest.raises(IndexError):
        timeline.time_of_next_event
    with pytest.raises(IndexError):
        timeline.next_event


def test_init_with_one_event():
    timeline = Timeline([("event 1", 1.)])

    assert set(["event 1"]) == timeline.events
    assert 1. == timeline.time_of_next_event
    assert "event 1" == timeline.next_event


def test_init_with_two_events():
    timeline = Timeline([("event 1", 1.), ("event 2", .25)])

    assert set(["event 1", "event 2"]) == timeline.events
    assert timeline.time_of_next_event == approx(.25)
    assert timeline.next_event == "event 2"


def test_non_zero_start():
    timeline = Timeline([("event 1", 1.), ("event 2", .25)], start=-1)
    assert timeline.time_of_next_event == approx(-.75)
    assert timeline.pop_until(0.) == [
        "event 2",
        "event 2",
        "event 2",
        "event 1",
        "event 2",
    ]


def test_pop_empty_timeline():
    timeline = Timeline()
    with pytest.raises(IndexError):
        timeline.pop()


def test_pop_events():
    timeline = Timeline([("event 1", 1.), ("event 2", .25)])
    for time in [.25, .5, .75]:
        assert timeline.pop() == "event 2"
        assert timeline.time == approx(time)
    assert timeline.pop() == "event 1"
    assert timeline.time == approx(1.)

    assert timeline.pop() == "event 2"
    assert timeline.time == approx(1.)


def test_pop_until():
    timeline = Timeline([("event 1", 1.), ("event 2", .5)])
    events = timeline.pop_until(.2)
    assert events == []
    assert timeline.time == approx(.2)

    events = timeline.pop_until(1.)
    assert events == ["event 2", "event 1", "event 2"]
    assert timeline.time == approx(1.)


def test_hashable_event():
    timeline = Timeline([(("event", 2), .5), (("event", 0), 1.)])
    assert ("event", 2) == timeline.pop()
    assert ("event", 0) == timeline.pop()
    assert ("event", 2) == timeline.pop()


def test_unhashable_event():
    (first_event, second_event) = (dict(foo="bar"), dict(bar="baz"))
    timeline = Timeline([(first_event, .5), (second_event, 1.)])
    assert first_event is timeline.pop()
    assert second_event is timeline.pop()
    assert first_event is timeline.pop()


def test_one_time_event():
    timeline = Timeline([("recurring-event", 1.)])
    timeline.add_one_time_event("one-timer", .1)
    events = timeline.pop_until(2.)
    assert events == ["one-timer", "recurring-event", "recurring-event"]


def test_repeated_events():
    (first_event, second_event) = (dict(foo="bar"), dict(bar="baz"))
    timeline = Timeline([(first_event, .5), (second_event, 1.), (first_event, .75)])
    assert first_event is timeline.pop()
    assert first_event is timeline.pop()
    assert second_event is timeline.pop()
    assert first_event is timeline.pop()

    timeline = Timeline([(first_event, .5), (second_event, 1.), (first_event, 1.)])
    assert first_event is timeline.pop()
    assert second_event is timeline.pop()
    assert first_event is timeline.pop()
    assert first_event is timeline.pop()

    timeline = Timeline([(first_event, .5), (first_event, 1.), (second_event, 1.)])
    assert first_event is timeline.pop()
    assert first_event is timeline.pop()
    assert second_event is timeline.pop()
    assert first_event is timeline.pop()
