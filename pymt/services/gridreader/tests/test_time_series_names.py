import pytest

from pymt.services.gridreader import time_series_names as tsn


def test_split_valid():
    parts = tsn.split("sea_floor_surface__elevation@t=123")
    assert parts == ("sea_floor_surface__elevation", 123)


def test_split_no_time_stamp():
    with pytest.raises(tsn.TimeSeriesNameError):
        tsn.split("sea_floor_surface__elevation")


def test_split_bad_time_stamp():
    with pytest.raises(tsn.TimeSeriesNameError):
        tsn.split("sea_floor_surface__elevation@t=12.2")


def test_split_time_stamp_with_leading_zeros():
    parts = tsn.split("sea_floor_surface__elevation@t=0001")
    assert parts[1] == 1


def test_unsplit():
    name = tsn.unsplit("ice_surface__temperature", 1)
    assert name == "ice_surface__temperature@t=1"


def test_unsplit_str_time_stamp():
    name = tsn.unsplit("ice_surface__temperature", "0001")
    assert name == "ice_surface__temperature@t=1"


def test_unsplit_float_time_stamp():
    with pytest.raises(tsn.TimeStampError):
        name = tsn.unsplit("ice_surface__temperature", "1.2")


def test_get_time_series_names():
    names = tsn.get_time_series_names(
        [
            "ice_surface__temperature@t=0",
            "ice_surface__temperature@t=1",
            "earth_surface__temperature",
        ]
    )
    assert names == set(["ice_surface__temperature"])


def test_get_time_series_names_empty():
    names = tsn.get_time_series_names(["ice_surface__temperature"])
    assert names == set()

    names = tsn.get_time_series_names([])
    assert names == set()


def test_get_time_series_names_ignore_bad_names():
    names = tsn.get_time_series_names(
        [
            "ice_surface__temperature@t=0",
            "ice_surface__temperature@t=1",
            "earth_surface__temperature@t=1.2",
            "sea_surface__temperature@t=",
        ]
    )
    assert names == set(["ice_surface__temperature"])


def test_sort_ascending_is_default():
    names = [
        "ice_surface__temperature@t=1",
        "ice_surface__temperature@t=2",
        "ice_surface__temperature@t=0",
        "ice_surface__temperature@t=10",
        "earth_surface__temperature",
    ]
    assert tsn.sort_time_series_names(names) == tsn.sort_time_series_names(
        names, ordering="ascending"
    )


def test_sort_ascending():
    names = tsn.sort_time_series_names(
        [
            "ice_surface__temperature@t=1",
            "ice_surface__temperature@t=0",
            "ice_surface__temperature@t=10",
            "ice_surface__temperature@t=2",
            "earth_surface__temperature",
        ],
        ordering="ascending",
    )
    assert names == {
        "ice_surface__temperature": [
            "ice_surface__temperature@t=0",
            "ice_surface__temperature@t=1",
            "ice_surface__temperature@t=2",
            "ice_surface__temperature@t=10",
        ]
    }


def test_sort_descending():
    names = tsn.sort_time_series_names(
        [
            "ice_surface__temperature@t=1",
            "ice_surface__temperature@t=2",
            "ice_surface__temperature@t=0",
            "earth_surface__temperature",
        ],
        ordering="descending",
    )
    assert names == {
        "ice_surface__temperature": [
            "ice_surface__temperature@t=2",
            "ice_surface__temperature@t=1",
            "ice_surface__temperature@t=0",
        ]
    }


def test_sort_no_ordering():
    names = [
        "ice_surface__temperature@t=1",
        "ice_surface__temperature@t=2",
        "earth_surface__temperature",
        "ice_surface__temperature@t=0",
    ]
    assert tsn.sort_time_series_names(names, ordering=None) == dict(
        ice_surface__temperature=[
            "ice_surface__temperature@t=1",
            "ice_surface__temperature@t=2",
            "ice_surface__temperature@t=0",
        ]
    )
