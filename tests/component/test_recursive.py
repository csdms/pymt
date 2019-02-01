import os

from six.moves import xrange

from pymt.component.component import Component
from pymt.framework.services import del_component_instances


def test_no_events(with_no_components):
    del_component_instances(["air_port", "earth_port"])

    air = Component("AirPort", name="air_port", uses=[], provides=[], events=[])
    earth = Component(
        "EarthPort", name="earth_port", uses=["air_port"], provides=[], events=[]
    )
    earth.connect("air_port", air)
    air.connect("earth_port", earth)
    earth.go()

    assert air._port.current_time == 100.0
    assert earth._port.current_time == 100.0


def test_print_events(tmpdir, with_no_components):
    air_init_string = """
name: air_port
class: AirPort
print:
- name: air__temperature
  interval: 25.
  format: vtk
"""
    earth_init_string = """
name: earth_port
class: EarthPort
print:
- name: glacier_top_surface__slope
  interval: 20.
  format: vtk
"""
    with tmpdir.as_cwd():
        del_component_instances(["air_port", "earth_port"])

        air = Component.from_string(air_init_string)
        earth = Component.from_string(earth_init_string)
        earth.connect("air_port", air)
        air.connect("earth_port", earth)
        earth.go()

        for i in xrange(5):
            assert os.path.isfile("glacier_top_surface__slope_%04d.vtu" % i)
            os.remove("glacier_top_surface__slope_%04d.vtu" % i)
        for i in xrange(4):
            assert os.path.isfile("air__temperature_%04d.vtu" % i)
            os.remove("air__temperature_%04d.vtu" % i)

        del_component_instances(["air_port", "earth_port"])

        air = Component.from_string(air_init_string)
        earth = Component.from_string(earth_init_string)
        earth.connect("air_port", air)
        air.connect("earth_port", earth)
        air.go()

        for i in xrange(5):
            assert os.path.isfile("glacier_top_surface__slope_%04d.vtu" % i)
        for i in xrange(4):
            assert os.path.isfile("air__temperature_%04d.vtu" % i)
