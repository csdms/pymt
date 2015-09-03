__all__ = []

from os import path
import sys
import importlib
from glob import glob

from .framework.bmi_bridge import bmi_factory


csdms_module = importlib.import_module('csdms')
files = glob(path.join(csdms_module.__path__[0], '*so'))
_COMPONENT_NAMES = (path.splitext(path.basename(f))[0] for f in files)


for name in _COMPONENT_NAMES:
    try:
        module = importlib.import_module('.'.join(['csdms', name]))
    except ImportError:
        pass
    else:
        if name in module.__dict__:
            setattr(sys.modules[__name__], name, bmi_factory(module.__dict__[name]))
            __all__.append(name)
