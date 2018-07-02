"""Access to framework services.
"""
import warnings


_COMPONENT_CLASSES = {}
_COMPONENT_INSTANCES = {}


def register_component_classes(components, **kwds):
    """Register a list of components with the framework.

    Parameters
    ----------
    components : list
        Component names to register.
    if_exists : {'raise', 'warn', 'pass', 'clobber'}, optional
        What to do if the class is already registered.

    See Also
    --------
    :func:`register_component_class` : Register just a single component.
    """
    for name in components:
        register_component_class(name, **kwds)


def register_component_class(name, if_exists="raise"):
    """Register a component with the framework.

    Add the component class, *name*, to the list of framework services. The
    component name should be the fully-qualified name of a Python class.

    Parameters
    ----------
    name : str
        Name of component to register.
    if_exists : {'raise', 'warn', 'pass', 'clobber'}, optional
        What to do if the class is already registered.

    Raises
    ------
    ValueError
        If the class is already registered with the framework.
    ImportError
        If there is a problem importing any part of *name*.

    Notes
    -----
    This function will try to import *name* as though it were a fully-qualified
    name of a Python class. That is, if *name* were `foo.bar.Baz`, try the
    following::

        from foo.bar import Baz

    Examples
    --------
    >>> from pymt.framework.services import (
    ...     del_services,
    ...     register_component_class,
    ...     get_component_class
    ... )

    >>> del_services()
    >>> register_component_class('pymt.testing.services.AirPort')
    >>> get_component_class('AirPort')
    <class 'pymt.testing.services.AirPort'>

    Raise an ImportError if the component class could not be loaded.

    >>> register_component_class('pymt.testing.services.NotAClass') # doctest : +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ImportError: cannot import component NotAClass from pymt.testing.services
    >>> register_component_class('pymt.not.a.module.AirPort') # doctest : +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ValueError: component class exists (AirPort)
    """
    parts = name.split(".")
    module_name, cls_name = (".".join(parts[:-1]), parts[-1])

    if cls_name in _COMPONENT_CLASSES:
        if if_exists == "raise":
            raise ValueError("component class exists (%s)" % cls_name)
        elif if_exists == "warn":
            warnings.warn("component class exists (%s)" % cls_name)
            return
        elif if_exists == "pass":
            return

    mod = __import__(module_name, fromlist=[cls_name])
    try:
        _COMPONENT_CLASSES[cls_name] = getattr(mod, cls_name)
    except (KeyError, AttributeError):
        raise ImportError(
            "cannot import component %s from %s" % (cls_name, module_name)
        )


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
    >>> from pymt.framework.services import (
    ...     del_services,
    ...     register_component_class,
    ...     get_component_instance
    ... )

    >>> del_services()
    >>> from pymt.testing.services import AirPort
    >>> air_port = AirPort()
    >>> register_component_instance('air_port', air_port)
    >>> air_port is get_component_instance('air_port')
    True
    """
    if name in _COMPONENT_INSTANCES:
        raise ValueError("component instance exists (%s)" % name)
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

    Instantiate a registered class and register that instance with the framework
    as *instance_name*.

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
    >>> from pymt.framework.services import (
    ...     del_services,
    ...     register_component_class,
    ...     instantiate_component,
    ...     get_component_instance
    ... )

    >>> del_services()
    >>> register_component_class('pymt.testing.services.AirPort')
    >>> air_port = instantiate_component('AirPort', 'air_port')
    >>> air_port is get_component_instance('air_port')
    True
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


def del_services():
    del_component_instances(get_component_instance_names())
    for name in list(_COMPONENT_CLASSES.keys()):
        del _COMPONENT_CLASSES[name]


def get_component_instance_names():
    """Names of all instances.

    Returns
    -------
    list
        Names of all the instanciated components.
    """
    return list(_COMPONENT_INSTANCES.keys())
