def setup():
    from cmt.framework.services import (register_component_classes,
                                        del_services)


    del_services()

    register_component_classes(["cmt.testing.services.AirPort",
                                "cmt.testing.services.EarthPort"])
