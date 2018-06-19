from nose.tools import assert_equal

from pymt.framework.bmi_bridge import _BmiCap


class SimpleTimeBmi():
    def get_time_units(self):
        return 'h'

    def get_start_time(self):
        return 1.

    def get_current_time(self):
        return 10.5

    def get_end_time(self):
        return 72

    def get_time_step(self):
        return 0.25


class Bmi(_BmiCap):
    _cls = SimpleTimeBmi


def test_time_wrap():
    """Test wrapping BMI time methods."""
    bmi = Bmi()

    assert_equal(bmi.get_time_units(), 'h')
    assert_equal(bmi.get_start_time(), 1.)
    assert_equal(bmi.get_current_time(), 10.5)
    assert_equal(bmi.get_end_time(), 72.)
    assert_equal(bmi.get_time_step(), .25)
    assert_equal(bmi.time_units, 'h')


def test_time_conversion():
    """Test unit conversion through units keyword."""
    bmi = Bmi()

    assert_equal(bmi.get_start_time(units='h'), 1.)

    assert_equal(bmi.get_start_time(units='min'), 60.)
    assert_equal(bmi.get_current_time(units='min'), 630.)
    assert_equal(bmi.get_end_time(units='d'), 3)


def test_change_time_units():
    """Test changing a component's time units."""
    bmi = Bmi()

    assert_equal(bmi.time_units, 'h')
    bmi.time_units = 'min'
    assert_equal(bmi.time_units, 'min')

    assert_equal(bmi.get_start_time(), 60.)
    assert_equal(bmi.get_current_time(), 630.)
    assert_equal(bmi.get_end_time(), 72 * 60)

    assert_equal(bmi.get_start_time(units='h'), 1.)
    assert_equal(bmi.get_current_time(units='h'), 10.5)
    assert_equal(bmi.get_end_time(units='h'), 72)
