import os

from six.moves import xrange

from pymt.component.component import Component


def test_print_events(tmpdir, with_no_components):
    air = Component.load(
        """
name: air_port
class: AirPort
print:
- name: air__temperature
  interval: 25.
  format: vtk
"""
    )
    earth = Component.load(
        """
name: earth_port
class: EarthPort
print:
- name: glacier_top_surface__slope
  interval: 20.
  format: vtk
"""
    )
    with tmpdir.as_cwd():
        earth.connect(
            "air_port",
            air,
            vars_to_map=[
                ("glacier_top_surface__slope", "air__temperature"),
                ("earth_surface__temperature", "air__temperature"),
            ],
        )
        earth.go()

        for i in xrange(5):
            assert os.path.isfile("glacier_top_surface__slope_%04d.vtu" % i)
        for i in xrange(4):
            assert os.path.isfile("air__temperature_%04d.vtu" % i)
