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
    earth.go()

    assert earth._port.current_time == 100.0
    assert air._port.current_time == 100.0


def test_print_events(tmpdir, with_no_components):
    del_component_instances(["air_port", "earth_port"])

    air = Component.from_string(
        """
name: air_port
class: AirPort
print:
- name: air__temperature
  interval: 25.
  format: nc
"""
    )
    earth = Component.from_string(
        """
name: earth_port
class: EarthPort
print:
- name: glacier_top_surface__slope
  interval: 20.
  format: nc
"""
    )
    earth.connect("air_port", air)

    with tmpdir.as_cwd():
        earth.go()

        assert os.path.isfile("glacier_top_surface__slope.nc")
        assert os.path.isfile("air__temperature.nc")
