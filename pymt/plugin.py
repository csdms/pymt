"""Dynamically find and load plugins."""
from __future__ import print_function

__all__ = []

import os
import logging
import importlib
from glob import glob

from .framework.bmi_bridge import bmi_factory
from .babel import setup_babel_environ


def load_plugin(entry_point, callback=None):
    """Load a generic plugin.

    Parameters
    ----------
    entry_point : str
        A entry point specify for the plugin. The specifier should be a
        dotted module name followed by a ``:`` and an identifier nameing an
        object within the module.
    callback : func
        If provided, this function will be called on the plugin and the
        result returned.

    Returns
    -------
    object
        The plugin.
    """
    module_name, cls_name = entry_point.split(':')

    plugin = None
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        logging.info('Unable to import {module}.'.format(module=module_name))
    else:
        try:
            plugin = module.__dict__[cls_name]
        except KeyError:
            logging.info('{plugin} not contained in {module}.'.format(
                plugin=cls_name, module=module_name))
    if callback and plugin:
        plugin = callback(plugin)

    return plugin


def load_all_plugins(entry_points=[], callback=None):
    """Load multiple plugins.

    Parameters
    ----------
    entry_points : iterable of str, optional
        A list of plugins to load.
    callback : func, optional
        A callback function that is called on each loaded plugin.

    Returns
    -------
    list
        A list of loaded plugins.
    """
    try:
        entry_points += os.environ['PYMT_PLUGINS'].split(';')
    except KeyError:
        pass

    all_plugins = []
    for entry_point in entry_points:
        all_plugins.append(load_plugin(entry_point, callback=callback))

    return all_plugins


def discover_csdms_plugins():
    """Look for plugins in the csdms package.

    Returns
    -------
    list or str
        Entry point specifications.
    """
    entry_points = []
    try:
        csdms_module = importlib.import_module('csdms')
    except ImportError:
        logging.info('Unable to import {module}.'.format(module='csdms'))
    else:
        files = glob(os.path.join(csdms_module.__path__[0], '*so'))
        for path in files:
            name, ext = os.path.splitext(os.path.basename(path))
            entry_points.append('csdms.{name}:{name}'.format(name=name))

    return entry_points


def load_csdms_plugins():
    """Load all available csdms plugins.

    Returns
    -------
    list
        BMI plugins.
    """
    setup_babel_environ()
    entry_points = discover_csdms_plugins()
    return load_all_plugins(entry_points, callback=bmi_factory)
