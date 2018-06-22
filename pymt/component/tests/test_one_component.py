from six.moves import xrange
from nose.tools import assert_equal

from pymt.component.component import Component
from pymt.testing.assertions import assert_isfile_and_remove
from pymt.framework.services import del_component_instances


def test_no_events(setup):
    del_component_instances(["AirPort"])

    comp = Component("AirPort", uses=[], provides=[], events=[])
    comp.go()
    assert_equal(comp._port.current_time, 100.)


def test_from_string(setup):
    del_component_instances(["air_port"])

    contents = """
name: air_port
class: AirPort
    """
    comp = Component.from_string(contents)
    comp.go()
    assert_equal(comp._port.current_time, 100.)


def test_print_events(setup):
    del_component_instances(["earth_port"])

    contents = """
name: earth_port
class: EarthPort
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
    assert_isfile_and_remove("earth_surface__temperature.nc")
    assert_isfile_and_remove("glacier_top_surface__slope.nc")
    for i in xrange(5):
        assert_isfile_and_remove("earth_surface__density_%04d.vtu" % i)


def test_rerun(setup):
    del_component_instances(["AirPort"])

    comp = Component("AirPort", uses=[], provides=[], events=[])
    comp.go()
    assert_equal(comp._port.current_time, 100.)

    comp.go()
    assert_equal(comp._port.current_time, 100.)


def test_rerun_with_print(setup):
    del_component_instances(["earth_port"])

    contents = """
name: earth_port
class: EarthPort

print:
- name: earth_surface__temperature
  interval: 20
  format: vtk
    """
    comp = Component.from_string(contents)
    comp.go()

    assert_equal(comp._port.current_time, 100.)
    for i in xrange(5):
        assert_isfile_and_remove("earth_surface__temperature_%04d.vtu" % i)

    del_component_instances(["earth_port"])

    comp = Component.from_string(contents)
    comp.go()

    assert_equal(comp._port.current_time, 100.)
    for i in xrange(5):
        assert_isfile_and_remove("earth_surface__temperature_%04d.vtu" % i)
