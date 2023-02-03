import pytest


@pytest.fixture(scope="function")
def with_two_components():
    from pymt.framework.services import (
        del_services,
        instantiate_component,
        register_component_classes,
    )

    del_services()

    register_component_classes(
        [
            "pymt.testing.services.AirPort",
            "pymt.testing.services.EarthPort",
            "pymt.testing.services.WaterPort",
        ]
    )
    instantiate_component("AirPort", "air_port")
    instantiate_component("EarthPort", "earth_port")
    instantiate_component("WaterPort", "water_port")
