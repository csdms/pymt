from __future__ import print_function

__all__ = []

import os
import sys
import warnings
import importlib
from glob import glob

from .framework.bmi_bridge import bmi_factory
from .babel import setup_babel_environ


def import_csdms_components():
    debug = os.environ.get('PYMT_DEBUG', False)
    setup_babel_environ()
    if debug:
        print('Importing components with the following environment')
        for k, v in os.environ.items():
            print('- {key}: {val}'.format(key=k, val=v))

    try:
        csdms_module = importlib.import_module('csdms')
    except ImportError:
        warnings.warn('Unable to import csdms. Not loading components.')
    else:
        if debug:
            print('imported csdms module')
        files = glob(os.path.join(csdms_module.__path__[0], '*so'))
        _COMPONENT_NAMES = [
            os.path.splitext(os.path.basename(f))[0] for f in files]

        if debug:
            print('found the following components')
            for name in _COMPONENT_NAMES:
                print('- {name}'.format(name=name))

        for name in _COMPONENT_NAMES:
            module_name = '.'.join(['csdms', name])
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                if debug:
                    print('unable to import {mod}'.format(mod=module_name))
            else:
                if debug:
                    print('imported {mod}'.format(mod=module_name))

                if name in module.__dict__:
                    try:
                        setattr(sys.modules[__name__], name,
                                bmi_factory(module.__dict__[name]))
                        __all__.append(name)
                    except Exception as err:
                        print('warning: found csdms.{name} but was unable '
                              'to wrap it'.format(name=name))
                        if debug:
                            print(err)


import_csdms_components()
