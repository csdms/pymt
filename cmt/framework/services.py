"""Access to framework services.
"""
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
    """Register a list of components with the framework.

    Parameters
    ----------
    components : list
        Component names to register.

    See Also
    --------
    :func:`register_component_class` : Register just a single component.
    """
    for name in components:
        register_component_class(name)


def register_component_class(name):
    """Register a component with the framework.

    Add the component class, *name*, to the list of framework services. The component name should be the
    fully-qualified name of a Python class.

    Parameters
    ----------
    name : str
        Name of component to register.

    Raises
    ------
    ValueError
        If the class is already registered with the framework.
    ImportError
        If there is a problem importing any part of *name*.

    Notes
    -----
    This function will try to import *name* as though it were a fully-qualified name of a Python class. That is,
    if *name* were `foo.bar.Baz`, try the following::

        from foo.bar import Baz

    Examples
    --------
    >>> register_component_class('cmt.testing.services.AirPort')
    >>> get_component_class('AirPort')
    <class 'services.AirPort'>

    Raise an ImportError if the component class could not be loaded.

    >>> register_component_class('cmt.testing.services.NotAClass') # doctest : +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ImportError: cannot import name NotAClass from cmt.testing.services
    >>> register_component_class('cmt.not.a.module.AirPort') # doctest : +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ImportError: No module named not
    """
    parts = name.split('.')
    module_name, cls_name = ('.'.join(parts[:-1]), parts[-1])

    if cls_name in _COMPONENT_CLASSES:
        raise ValueError('component class exists (%s)' % cls_name)
    else:
        mod = __import__(module_name, fromlist=[cls_name])
        try:
            _COMPONENT_CLASSES[cls_name] = getattr(mod, cls_name)
        except (KeyError, AttributeError):
            raise ImportError('cannot import component %s from %s' %
                              (cls_name, module_name))


def register_component_instance(name, instance):
    """Register a component instance with the framework.

    Parameters
    ----------
    name : str
        Name of the component instance.
    instance : object
        Component instance.

    Raises
    ------
    ValueError
        If *name* is already registered with the framework.

    Examples
    --------
    >>> from cmt.testing.services import AirPort
    >>> air_port = AirPort()
    >>> register_component_instance('air_port', air_port)
    >>> air_port is get_component_instance('air_port')
    True
    """
    if name in _COMPONENT_INSTANCES:
        raise ValueError('component instance exists (%s)' % name)
    else:
        _COMPONENT_INSTANCES[name] = instance


def get_component_class(name):
    """Get a registered component class by name.

    Parameters
    ----------
    name : str
        Name of the registered class.

    Returns
    -------
    class
        The registered class.

    Raises
    ------
    KeyError
        If the *name* is not registered with the framework.

    See Also
    --------
    :func:`register_component_class`
    """
    return _COMPONENT_CLASSES[name]


def instantiate_component(cls_name, instance_name):
    """Instantiate a registered component class.

    Instantiate a registered class and register that instance with the framework as *instance_name*.

    Parameters
    ----------
    cls_name : str
        Name of the registered class.
    instance_name : str
        Name of the new instance.

    Returns
    -------
    object
        An instance of the registered class.

    Examples
    --------
    >>> register_component_class('cmt.testing.services.AirPort')
    >>> air_port = instantiate_component('AirPort', 'air_port')
    >>> air_port is get_component_instance('air_port')
    """
    register_component_instance(instance_name, get_component_class(cls_name)())
    return get_component_instance(instance_name)


def get_component_instance(name):
    """Get a registered instance from the framework.

    Parameters
    ----------
    name : str
        Name of the registered instance.

    Returns
    -------
    object
        The registered instance.

    Raises
    ------
    KeyError
        If *name* is not registered with the framework.

    See Also
    --------
    :func:`instantiate_component`
    """
    return _COMPONENT_INSTANCES[name]


def del_component_instance(name):
    """Remove an instance by name.

    Parameters
    ----------
    name : str
        Component instance.

    See Also
    --------
    :func:`del_component_instances`
    """
    try:
        del _COMPONENT_INSTANCES[name]
    except KeyError:
        pass


def del_component_instances(names):
    """Remove a list of instances by name.

    Parameters
    ----------
    names : list
        Component instance names.

    See Also
    --------
    :func:`del_component_instance`
    """
    for name in names:
        del_component_instance(name)


def get_component_instance_names():
    """Names of all instances.

    Returns
    -------
    list
        Names of all the instanciated components.
    """
    return _COMPONENT_INSTANCES.keys()
