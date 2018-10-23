import os

from pymt.component.component import Component
from pymt.framework.services import del_component_instances
from six.moves import xrange


def test_no_events(with_no_components):
    del_component_instances(["AirPort"])

    comp = Component("AirPort", uses=[], provides=[], events=[])
    comp.go()
    assert comp._port.current_time == 100.0


def test_from_string(with_no_components):
    del_component_instances(["air_port"])

    contents = """
name: air_port
class: AirPort
    """
    comp = Component.from_string(contents)
    comp.go()
    assert comp._port.current_time == 100.0


def test_print_events(tmpdir, with_no_components):
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
    with tmpdir.as_cwd():
        comp = Component.from_string(contents)
        comp.go()

        assert comp._port.current_time == 100.0
        assert os.path.isfile("earth_surface__temperature.nc")
        assert os.path.isfile("glacier_top_surface__slope.nc")
        for i in xrange(5):
            assert os.path.isfile("earth_surface__density_%04d.vtu" % i)


def test_rerun(with_no_components):
    del_component_instances(["AirPort"])

    comp = Component("AirPort", uses=[], provides=[], events=[])
    comp.go()
    assert comp._port.current_time == 100.0

    comp.go()
    assert comp._port.current_time == 100.0


def test_rerun_with_print(tmpdir, with_no_components):
    del_component_instances(["earth_port"])

    contents = """
name: earth_port
class: EarthPort

print:
- name: earth_surface__temperature
  interval: 20
  format: vtk
    """
    with tmpdir.as_cwd():
        comp = Component.from_string(contents)
        comp.go()

        assert comp._port.current_time == 100.0
        for i in xrange(5):
            assert os.path.isfile("earth_surface__temperature_%04d.vtu" % i)
            os.remove("earth_surface__temperature_%04d.vtu" % i)

        del_component_instances(["earth_port"])

        comp = Component.from_string(contents)
        comp.go()

        assert comp._port.current_time == 100.0
        for i in xrange(5):
            assert os.path.isfile("earth_surface__temperature_%04d.vtu" % i)
