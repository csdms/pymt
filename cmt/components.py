__all__ = []

import os
import sys
import importlib
from glob import glob

from .framework.bmi_bridge import bmi_factory


def prepend_path(env, var, p, sep=os.pathsep):
    try:
        env[var] = sep.join([p, env[var]])
    except KeyError:
        env[var] = p

    return p


def set_env():
    import os
    import subprocess
    import warnings

    try:
        prefix = subprocess.check_output(['csdms-config', '--var',
                                          'PREFIX']).strip()
    except subprocess.CalledProcessError:
        warnings.warn('Unable to locate or run csdms-config program.')
    else:
        prepend_path(os.environ, 'SIDL_DLL_PATH',
                     os.path.join(prefix, 'share', 'cca'), sep=';')

    try:
        libdir = subprocess.check_output(['cca-spec-babel-config', '--var',
                                          'CCASPEC_BABEL_LIBS']).strip()
    except subprocess.CalledProcessError:
        warnings.warn('Unable to locate or run cca-spec-babel-config program.')
    else:
        prepend_path(os.environ, 'LD_LIBRARY_PATH', libdir)


set_env()

csdms_module = importlib.import_module('csdms')
files = glob(os.path.join(csdms_module.__path__[0], '*so'))
_COMPONENT_NAMES = (os.path.splitext(os.path.basename(f))[0] for f in files)


for name in _COMPONENT_NAMES:
    try:
        module = importlib.import_module('.'.join(['csdms', name]))
    except ImportError:
        pass
    else:
        if name in module.__dict__:
            setattr(sys.modules[__name__], name, bmi_factory(module.__dict__[name]))
            __all__.append(name)
