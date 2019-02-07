import numpy as np
import pytest

from pytest import approx, raises

from pymt.framework.timeinterp import TimeInterpolator


def test_timeinterp():
    interp = TimeInterpolator(((0., 1.), (1., 2.), (2., 3.)))
    assert interp(.5) == approx(1.5)
    assert interp(1.75) == approx(2.75)


def test_timeinterp_with_scalars():
    interp = TimeInterpolator(((0., 1.),))
    with raises(ValueError):
        assert interp(.5) == approx(1.5)
    interp.add_data(((1., 2.),))
    assert interp(.5) == approx(1.5)


def test_timeinterp_add_data():
    interp = TimeInterpolator()
    interp.add_data(((0., 1.),))
    interp.add_data(((1., 2.),))
    assert interp(.5) == approx(1.5)


def test_timeinterp_multiple_interps():
    interp = TimeInterpolator()
    interp.add_data(((0., 1.), (1., 2.)))
    assert interp(.5) == approx(1.5)

    interp.add_data(((2., 3.),))
    assert interp(.5) == approx(1.5)
    assert interp(2.5) == approx(3.5)


def test_timeinterp_interpolate_method():
    interp = TimeInterpolator(((0., 1.), (1., 2.), (2., 3.)))
    assert interp.interpolate(.5) == approx(1.5)
    assert interp.interpolate(1.75) == approx(2.75)


def test_timeinterp_with_arrays():
    shape = (2, 3)
    arr = np.ones(shape, dtype=float)
    interp = TimeInterpolator(((0., arr * 1), (1., arr * 2), (2., arr * 3)))

    assert interp(.5) == approx(np.full(shape, 1.5))
    assert interp(1.75) == approx(np.full(shape, 2.75))


def test_timeinterp_with_dict_items():
    shape = (2, 3)
    data = {
        0.0: np.full(shape, 1.0),
        1.0: np.full(shape, 2.0),
        2.0: np.full(shape, 3.0),
    }
    interp = TimeInterpolator(data.items())

    assert interp(.5) == approx(np.full(shape, 1.5))
    assert interp(1.75) == approx(np.full(shape, 2.75))


@pytest.mark.parametrize("method", TimeInterpolator.METHODS)
def test_interp_on_a_point(method):
    interp = TimeInterpolator(((0., 1.), (1., 2.), (2., 3.), (3., 4.)), method=method)
    assert interp(2.0) == approx(3.0)


@pytest.mark.parametrize("method", TimeInterpolator.METHODS)
def test_interp_between_points(method):
    interp = TimeInterpolator(((0., 1.), (1., 2.), (2., 3.), (3., 4.)), method=method)
    assert 3.0 <= interp(2.5) <= 4.0


@pytest.mark.parametrize("method", TimeInterpolator.METHODS)
def test_interp_outside_range(method):
    interp = TimeInterpolator(((0., 1.), (1., 2.), (2., 3.), (3., 4.)), method=method)
    assert np.isfinite(interp(4.5)) and interp(4.5) >= 4.0


@pytest.mark.parametrize("method", TimeInterpolator.METHODS)
def test_interp_below_range(method):
    interp = TimeInterpolator(((0., 4.), (1., 3.), (2., 2.), (3., 1.)), method=method)
    assert np.isfinite(interp(-0.5)) and interp(-0.5) >= 4.0


@pytest.mark.parametrize("method", TimeInterpolator.METHODS)
def test_interp_with_fill_value(method):
    interp = TimeInterpolator(((0., 1.), (1., 2.), (2., 3.), (3., 4.)), method=method, fill_value=-1.0)
    assert interp(4.5) == approx(-1.0)
    assert interp(-0.5) == approx(-1.0)
