#! /usr/bin/env python
import pytest
from pytest import approx

from pymt.timeline import Timeline


def test_init_without_args():
    timeline = Timeline()
    assert 0.0 == timeline.time
    assert set() == timeline.events

    with pytest.raises(IndexError):
        timeline.time_of_next_event
    with pytest.raises(IndexError):
        timeline.next_event


def test_init_with_one_event():
    timeline = Timeline([("event 1", 1.0)])

    assert {"event 1"} == timeline.events
    assert 1.0 == timeline.time_of_next_event
    assert "event 1" == timeline.next_event


def test_init_with_two_events():
    timeline = Timeline([("event 1", 1.0), ("event 2", 0.25)])

    assert {"event 1", "event 2"} == timeline.events
    assert timeline.time_of_next_event == approx(0.25)
    assert timeline.next_event == "event 2"


def test_non_zero_start():
    timeline = Timeline([("event 1", 1.0), ("event 2", 0.25)], start=-1)
    assert timeline.time_of_next_event == approx(-0.75)
    assert timeline.pop_until(0.0) == [
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
    timeline = Timeline([("event 1", 1.0), ("event 2", 0.25)])
    for time in [0.25, 0.5, 0.75]:
        assert timeline.pop() == "event 2"
        assert timeline.time == approx(time)
    assert timeline.pop() == "event 1"
    assert timeline.time == approx(1.0)

    assert timeline.pop() == "event 2"
    assert timeline.time == approx(1.0)


def test_pop_until():
    timeline = Timeline([("event 1", 1.0), ("event 2", 0.5)])
    events = timeline.pop_until(0.2)
    assert events == []
    assert timeline.time == approx(0.2)

    events = timeline.pop_until(1.0)
    assert events == ["event 2", "event 1", "event 2"]
    assert timeline.time == approx(1.0)


def test_hashable_event():
    timeline = Timeline([(("event", 2), 0.5), (("event", 0), 1.0)])
    assert ("event", 2) == timeline.pop()
    assert ("event", 0) == timeline.pop()
    assert ("event", 2) == timeline.pop()


def test_unhashable_event():
    (first_event, second_event) = (dict(foo="bar"), dict(bar="baz"))
    timeline = Timeline([(first_event, 0.5), (second_event, 1.0)])
    assert first_event is timeline.pop()
    assert second_event is timeline.pop()
    assert first_event is timeline.pop()


def test_one_time_event():
    timeline = Timeline([("recurring-event", 1.0)])
    timeline.add_one_time_event("one-timer", 0.1)
    events = timeline.pop_until(2.0)
    assert events == ["one-timer", "recurring-event", "recurring-event"]


def test_repeated_events():
    (first_event, second_event) = (dict(foo="bar"), dict(bar="baz"))
    timeline = Timeline([(first_event, 0.5), (second_event, 1.0), (first_event, 0.75)])
    assert first_event is timeline.pop()
    assert first_event is timeline.pop()
    assert second_event is timeline.pop()
    assert first_event is timeline.pop()

    timeline = Timeline([(first_event, 0.5), (second_event, 1.0), (first_event, 1.0)])
    assert first_event is timeline.pop()
    assert second_event is timeline.pop()
    assert first_event is timeline.pop()
    assert first_event is timeline.pop()

    timeline = Timeline([(first_event, 0.5), (first_event, 1.0), (second_event, 1.0)])
    assert first_event is timeline.pop()
    assert first_event is timeline.pop()
    assert second_event is timeline.pop()
    assert first_event is timeline.pop()
