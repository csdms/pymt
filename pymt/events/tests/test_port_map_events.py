from numpy.testing import assert_array_equal

from pymt.events.manager import EventManager
from pymt.events.port import PortMapEvent, PortEvent
from pymt.events.chain import ChainEvent

from pymt.framework.services import get_component_instance


def assert_port_value_equal(port, name, value):
    assert_array_equal(port.get_value(name), value)


def test_one_event():
    foo = PortMapEvent(
        src_port="air_port",
        dst_port="earth_port",
        vars_to_map=[("earth_surface__temperature", "air__density")],
    )

    foo._src.initialize()
    foo._dst.initialize()

    with EventManager(((foo, 1.),)) as mngr:
        assert_port_value_equal(foo._src, "air__density", 0.)
        assert_port_value_equal(foo._dst, "earth_surface__temperature", 0.)


def test_chain():
    air = get_component_instance("air_port")
    earth = get_component_instance("earth_port")

    foo = ChainEvent(
        [
            PortEvent(port=air),
            PortMapEvent(
                dst_port=air,
                src_port=earth,
                vars_to_map=[("air__density", "earth_surface__temperature")],
            ),
        ]
    )

    bar = PortEvent(port=earth)

    with EventManager(((foo, 1.), (bar, 1.2))) as mngr:
        assert_port_value_equal(bar._port, "earth_surface__temperature", 0.)
        assert_port_value_equal(air, "air__density", 0.)

        mngr.run(1.)
        assert_port_value_equal(earth, "earth_surface__temperature", 0.)
        assert_port_value_equal(air, "air__density", 0.)

        mngr.run(2.)
        assert_port_value_equal(air, "air__density", 1.2)
