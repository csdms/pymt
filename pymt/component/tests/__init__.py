def setup():
    from pymt.framework.services import (register_component_classes,
                                         del_services)


    del_services()

    register_component_classes(["pymt.testing.services.AirPort",
                                "pymt.testing.services.EarthPort"])
