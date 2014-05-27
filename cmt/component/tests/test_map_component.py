from nose.tools import assert_equal

from cmt.component.component import Component
from cmt.testing.assertions import assert_isfile_and_remove


def test_print_events():
    air = Component.from_string("""
name: air_port
print:
- name: air__temperature
  interval: 25.
  format: vtk
""")
    earth = Component.from_string("""
name: earth_port
print:
- name: glacier_top_surface__slope
  interval: 20.
  format: vtk
""")
    earth.connect('air_port', air,
                  vars_to_map=[
                      ('glacier_top_surface__slope', 'air__temperature', ),
                      ('earth_surface__temperature', 'air__temperature', ),
                  ])
    earth.go()

    for i in xrange(5):
        assert_isfile_and_remove('glacier_top_surface__slope_%04d.vtu' % i)
    for i in xrange(4):
        assert_isfile_and_remove('air__temperature_%04d.vtu' % i)
