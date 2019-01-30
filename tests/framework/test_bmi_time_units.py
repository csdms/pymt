import pytest
from pytest import approx

from pymt.framework.bmi_bridge import _BmiCap

try:
    import cfunits
except ImportError:
    cfunits = None


class SimpleTimeBmi:
    def get_time_units(self):
        return "h"

    def get_start_time(self):
        return 1.0

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

    assert bmi.get_time_units() == "h"
    assert bmi.get_start_time() == approx(1.0)
    assert bmi.get_current_time() == approx(10.5)
    assert bmi.get_end_time() == approx(72.0)
    assert bmi.get_time_step() == approx(0.25)
    assert bmi.time_units == "h"


@pytest.mark.skipif(cfunits is None, reason="cfunits is not installed")
def test_time_conversion():
    """Test unit conversion through units keyword."""
    bmi = Bmi()

    assert bmi.get_start_time(units="h") == approx(1.0)

    assert bmi.get_start_time(units="min") == approx(60.0)
    assert bmi.get_current_time(units="min") == approx(630.0)
    assert bmi.get_end_time(units="d") == approx(3)


@pytest.mark.skipif(cfunits is None, reason="cfunits is not installed")
def test_change_time_units():
    """Test changing a component's time units."""
    bmi = Bmi()

    assert bmi.time_units == "h"
    bmi.time_units = "min"
    assert bmi.time_units == "min"

    assert bmi.get_start_time() == approx(60.0)
    assert bmi.get_current_time() == approx(630.0)
    assert bmi.get_end_time() == approx(72 * 60)

    assert bmi.get_start_time(units="h") == approx(1.0)
    assert bmi.get_current_time(units="h") == approx(10.5)
    assert bmi.get_end_time(units="h") == approx(72)
