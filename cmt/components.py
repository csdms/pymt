__all__ = []

import sys
import importlib

from .framework.bmi_bridge import bmi_factory


for name in ('Waves', 'Cem', 'DakotaPy', 'Hydrotrend'):
    try:
        module = importlib.import_module('.'.join(['csdms', name]))
    except ImportError:
        pass
    else:
        if name in module.__dict__:
            setattr(sys.modules[__name__], name, bmi_factory(module.__dict__[name]))
            __all__.append(name)
