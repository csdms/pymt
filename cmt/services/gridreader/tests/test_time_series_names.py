from nose.tools import (assert_equal, assert_set_equal, assert_raises,
                        assert_list_equal, assert_tuple_equal, assert_set_equal,
                        assert_dict_equal, assert_is)

from cmt.services.gridreader import time_series_names as tsn


def test_split_valid():
    parts = tsn.split('sea_floor_surface__elevation@t=123')
    assert_tuple_equal(parts, ('sea_floor_surface__elevation', 123))


def test_split_no_time_stamp():
    with assert_raises(tsn.TimeSeriesNameError):
        tsn.split('sea_floor_surface__elevation')


def test_split_bad_time_stamp():
    with assert_raises(tsn.TimeSeriesNameError):
        tsn.split('sea_floor_surface__elevation@t=12.2')


def test_split_time_stamp_with_leading_zeros():
    parts = tsn.split('sea_floor_surface__elevation@t=0001')
    assert_is(parts[1], 1)


def test_unsplit():
    name = tsn.unsplit('ice_surface__temperature', 1)
    assert_equal(name, 'ice_surface__temperature@t=1')


def test_unsplit_str_time_stamp():
    name = tsn.unsplit('ice_surface__temperature', '0001')
    assert_equal(name, 'ice_surface__temperature@t=1')


def test_unsplit_float_time_stamp():
    with assert_raises(tsn.TimeStampError):
        name = tsn.unsplit('ice_surface__temperature', '1.2')


def test_get_time_series_names():
    names = tsn.get_time_series_names([
        'ice_surface__temperature@t=0',
        'ice_surface__temperature@t=1',
        'earth_surface__temperature',
    ])
    assert_set_equal(names, set(['ice_surface__temperature']))


def test_get_time_series_names_empty():
    names = tsn.get_time_series_names(['ice_surface__temperature', ])
    assert_set_equal(names, set())

    names = tsn.get_time_series_names([])
    assert_set_equal(names, set())


def test_get_time_series_names_ignore_bad_names():
    names = tsn.get_time_series_names([
        'ice_surface__temperature@t=0',
        'ice_surface__temperature@t=1',
        'earth_surface__temperature@t=1.2',
        'sea_surface__temperature@t=',
    ])
    assert_set_equal(names, set(['ice_surface__temperature']))


def test_sort_ascending_is_default():
    names = ['ice_surface__temperature@t=1',
             'ice_surface__temperature@t=2',
             'ice_surface__temperature@t=0',
             'ice_surface__temperature@t=10',
             'earth_surface__temperature', ]
    assert_dict_equal(tsn.sort_time_series_names(names),
                      tsn.sort_time_series_names(names, ordering='ascending'))


def test_sort_ascending():
    names = tsn.sort_time_series_names([
        'ice_surface__temperature@t=1',
        'ice_surface__temperature@t=0',
        'ice_surface__temperature@t=10',
        'ice_surface__temperature@t=2',
        'earth_surface__temperature',
    ], ordering='ascending')
    assert_dict_equal(
        names,
        {'ice_surface__temperature': ['ice_surface__temperature@t=0',
                                      'ice_surface__temperature@t=1',
                                      'ice_surface__temperature@t=2',
                                      'ice_surface__temperature@t=10', ]})


def test_sort_descending():
    names = tsn.sort_time_series_names([
        'ice_surface__temperature@t=1',
        'ice_surface__temperature@t=2',
        'ice_surface__temperature@t=0',
        'earth_surface__temperature',
    ], ordering='descending')
    assert_dict_equal(
        names,
        {'ice_surface__temperature': ['ice_surface__temperature@t=2',
                                      'ice_surface__temperature@t=1',
                                      'ice_surface__temperature@t=0', ]})


def test_sort_no_ordering():
    names = ['ice_surface__temperature@t=1',
             'ice_surface__temperature@t=2',
             'earth_surface__temperature',
             'ice_surface__temperature@t=0', ]
    assert_dict_equal(
        tsn.sort_time_series_names(names, ordering=None),
        dict(ice_surface__temperature=['ice_surface__temperature@t=1',
                                       'ice_surface__temperature@t=2',
                                       'ice_surface__temperature@t=0', ]))


