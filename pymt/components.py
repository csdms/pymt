__all__ = []

import sys
from .plugin import load_csdms_plugins


for plugin in load_csdms_plugins():
    __all__.append(plugin.__name__)
    setattr(sys.modules[__name__], plugin.__name__, plugin)
