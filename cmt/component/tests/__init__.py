def setup():
    from cmt.framework.services import (register_component_classes,
                                        instantiate_component)


    register_component_classes(["cmt.testing.services.AirPort",
                                "cmt.testing.services.EarthPort"])
