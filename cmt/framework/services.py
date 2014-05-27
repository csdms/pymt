import sys
import imp
import warnings


_COMPONENT_CLASSES = {}
_COMPONENT_INSTANCES = {}


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

    try:
        (file, pathname, description) = imp.find_module(name, path)
    except ImportError:
        print name
        print path

    mod = imp.load_module(name, file, pathname, description)
    sys.modules['services'] = mod


def register_component_classes(components):
    #try:
    #    components = components.items()
    #except AttributeError:
    #    pass

    for name in components:
        register_component_class(name)


def _register_component_class(name, cls):
    if name in _COMPONENT_CLASSES:
        raise ValueError(name)
    else:
        _COMPONENT_CLASSES[name] = cls


def register_component_class(name):
    import sys
    print 'register %s' % name

    parts = name.split('.')
    cls_name = parts[-1]
    path = sys.path
    for name in parts[:-1]:
        (file, pathname, description) = imp.find_module(name, path)
        print 'load %s' % name
        mod = imp.load_module(name, file, pathname, description)
        try:
            path = mod.__path__
        except AttributeError:
            pass
            #raise
    #register_component_class(cls_name, mod.__dict__[cls_name])

    if cls_name in _COMPONENT_CLASSES:
        raise ValueError(cls_name)
    else:
        print 'register %s' % cls_name
        try:
            _COMPONENT_CLASSES[cls_name] = mod.__dict__[cls_name]
        except KeyError:
            print mod
            raise


def register_component_instance(name, instance):
    if name in _COMPONENT_INSTANCES:
        raise ValueError(name)
    else:
        _COMPONENT_INSTANCES[name] = instance


def get_component_class(name):
    return _COMPONENT_CLASSES[name]


def instantiate_component(cls_name, instance_name):
    register_component_instance(instance_name, get_component_class(cls_name)())
    return get_component_instance(instance_name)


def get_component_instance(name):
    return _COMPONENT_INSTANCES[name]
