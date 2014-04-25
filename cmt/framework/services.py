import sys
import imp
import warnings


def set_services(name, path=None, ifset='pass'):
    if 'services' in sys.modules:
        if ifset == 'pass':
            return
        elif ifset == 'warn':
            warnings.warn('services has already been set')
        elif ifset == 'raise':
            raise RuntimeError('services has already been set')
        elif ifset == 'clobber':
            pass
        else:
            raise ValueError('unrecognized option for ifset keyword')

    (file, pathname, description) = imp.find_module(name, path)
    mod = imp.load_module(name, file, pathname, description)
    sys.modules['services'] = mod
