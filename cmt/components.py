__all__ = []

import os
import sys
import warnings
import importlib
from glob import glob

from .framework.bmi_bridge import bmi_factory


class BabelConfigError(Exception):
    def __init__(self, prog):
        self._prog = prog

    def __str__(self):
        return self._prog


def prepend_env_path(var, path, sep=os.pathsep):
    """Prepend a path to an environment variable."""
    try:
        os.environ[var] = sep.join([path, os.environ[var]])
    except KeyError:
        os.environ[var] = path

    return path


def query_config_var(var, config='csdms-config'):
    """Get a configuration variable from a babel project."""
    import subprocess

    value = None

    try:
        value = subprocess.check_output([config, '--var', var]).strip()
    except subprocess.CalledProcessError:
        warnings.warn('Error running the {prog} program.'.format(prog=config))
    except OSError:
        warnings.warn('Unable to run {prog} program.'.format(prog=config))

    if value is None:
        raise BabelConfigError(config)

    return value


def setup_babel_environ():
    """Set up environment variables to load babelized components."""
    import os

    try:
        prefix = query_config_var('PREFIX', config='csdms-config')
        ccaspec_babel_libs = query_config_var('CCASPEC_BABEL_LIBS',
                                              config='cca-spec-babel-config')
    except BabelConfigError:
        warnings.warn('Unable to configure for babel. Not loading components.')
    else:
        prepend_env_path('SIDL_DLL_PATH', os.path.join(prefix, 'share', 'cca'),
                         sep=';')
        prepend_env_path('LD_LIBRARY_PATH', ccaspec_babel_libs)


setup_babel_environ()

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
            setattr(sys.modules[__name__], name,
                    bmi_factory(module.__dict__[name]))
            __all__.append(name)
