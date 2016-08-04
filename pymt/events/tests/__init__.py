def setup():
    from cmt.framework.services import (register_component_classes,
                                        instantiate_component, del_services)

    del_services()

    register_component_classes(["cmt.testing.services.AirPort",
                                "cmt.testing.services.EarthPort"])
    instantiate_component('AirPort', 'air_port')
    instantiate_component('EarthPort', 'earth_port')


