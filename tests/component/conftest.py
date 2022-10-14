import pytest


@pytest.fixture(scope="session")
def with_no_components():
    from pymt.framework.services import del_services, register_component_classes

    del_services()

    register_component_classes(
        ["pymt.testing.services.AirPort", "pymt.testing.services.EarthPort"]
    )
