__all__ = []

import sys

from .plugin import load_pymt_plugins

for plugin in load_pymt_plugins():
    __all__.append(plugin.__name__)
    setattr(sys.modules[__name__], plugin.__name__, plugin)

del sys, load_pymt_plugins, plugin
