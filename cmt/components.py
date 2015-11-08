__all__ = []

import os
import sys
import warnings
import importlib
from glob import glob

from .framework.bmi_bridge import bmi_factory
from .babel import setup_babel_environ


def import_csdms_components():
    setup_babel_environ()

    try:
        csdms_module = importlib.import_module('csdms')
    except ImportError:
        warnings.warn('Unable to import csdms. Not loading components.')
    else:
        files = glob(os.path.join(csdms_module.__path__[0], '*so'))
        _COMPONENT_NAMES = (
            os.path.splitext(os.path.basename(f))[0] for f in files)

        for name in _COMPONENT_NAMES:
            try:
                module = importlib.import_module('.'.join(['csdms', name]))
            except ImportError:
                pass
            else:
                if name in module.__dict__:
                    setattr(sys.modules[__name__], name,
                            bmi_factory(module.__dict__[name]))
                    __all__.append(name)


import_csdms_components()
