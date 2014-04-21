from nose.tools import assert_equal

from cmt.component.component import Component
from cmt.testing.assertions import assert_isfile_and_remove


def test_no_events():
    comp = Component('air_port', uses=[], provides=[], events=[])
    comp.go()
    assert_equal(comp._port.current_time, 100.)


def test_from_string():
    contents = """
name: air_port
    """
    comp = Component.from_string(contents)
    comp.go()
    assert_equal(comp._port.current_time, 100.)


def test_print_events():
    contents = """
name: earth_port

print:
- name: earth_surface__temperature
  interval: 0.1
  format: nc
- name: earth_surface__density
  interval: 20.
  format: vtk
- name: glacier_top_surface__slope
  interval: 0.3
  format: nc
    """
    comp = Component.from_string(contents)
    comp.go()

    assert_equal(comp._port.current_time, 100.)
    assert_isfile_and_remove('earth_surface__temperature.nc')
    assert_isfile_and_remove('glacier_top_surface__slope.nc')
    for i in xrange(5):
        assert_isfile_and_remove('earth_surface__density_%04d.vtu' % i)


def test_rerun():
    comp = Component('air_port', uses=[], provides=[], events=[])
    comp.go()
    assert_equal(comp._port.current_time, 100.)

    comp.go()
    assert_equal(comp._port.current_time, 100.)


def test_rerun_with_print():
    contents = """
name: earth_port

print:
- name: earth_surface__temperature
  interval: 20
  format: vtk
    """
    comp = Component.from_string(contents)
    comp.go()

    assert_equal(comp._port.current_time, 100.)
    for i in xrange(5):
        assert_isfile_and_remove('earth_surface__temperature_%04d.vtu' % i)

    comp = Component.from_string(contents)
    comp.go()

    assert_equal(comp._port.current_time, 100.)
    for i in xrange(5):
        assert_isfile_and_remove('earth_surface__temperature_%04d.vtu' % i)
