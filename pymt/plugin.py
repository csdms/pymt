"""Dynamically find and load plugins.

PyMT plugins are components that expose the CSDMS Basic
Model Interface and provide CSDMS Model Metadata. With
these two things, third-party components can be imported
into the PyMT modeling framework.

By default PyMT searches a package named `csdms`, if
it exists, for possible plugins that implement a BMI.
The corresponding model metadata for each plugin is
assumed to be located under `share/csdms` in a folder
named for that plugin. This is the file structure that
the CSDMS babelizer tool uses when wrapping models.

Although components written in Python can be processed
with the babelizer to bring them into PyMT, this
step should not be necessary as they are already
written in Python with a BMI. For these models,
plugins can be specified by a string that gives the
fully qualified name of the module (in dotted notation)
that contains the object followed by a colon and the
name of the class that implents the BMI. For example,

    pypkg.mymodule:MyPlugin

Standard plugins (those contained in the csdms package)
are automatically loaded while other plugins are
dynamically loaded the the pymt `load_plugin` function.
"""
from __future__ import print_function

import importlib
import logging
import os
from collections import OrderedDict, namedtuple
from glob import glob

import pkg_resources

from scripting import error, status

from .babel import setup_babel_environ
from .framework.bmi_bridge import bmi_factory

__all__ = []


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
    module_name, cls_name = entry_point.split(":")

    plugin = None
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        logging.info("Unable to import {module}.".format(module=module_name))
    else:
        try:
            plugin = module.__dict__[cls_name]
        except KeyError:
            logging.info(
                "{plugin} not contained in {module}.".format(
                    plugin=cls_name, module=module_name
                )
            )
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
        entry_points += os.environ["PYMT_PLUGINS"].split(";")
    except KeyError:
        pass

    all_plugins = []
    for entry_point in entry_points:
        all_plugins.append(load_plugin(entry_point, callback=callback))

    return all_plugins


def load_bmi_plugin(entry_point):
    """Load a plugin that implements as BMI.

    Parameters
    ----------
    entry_point : str
        A entry point specify for the plugin. The specifier should be a
        dotted module name followed by a ``:`` and an identifier nameing an
        object within the module.

    Returns
    -------
    object
        The BMI plugin.
    """
    return load_plugin(entry_point, callback=bmi_factory)


def discover_csdms_plugins():
    """Look for plugins in the csdms package.

    Returns
    -------
    list or str
        Entry point specifications.
    """
    entry_points = []
    try:
        csdms_module = importlib.import_module("csdms")
    except ImportError:
        logging.info("Unable to import {module}.".format(module="csdms"))
    else:
        files = glob(os.path.join(csdms_module.__path__[0], "*so"))
        for path in files:
            name, _ = os.path.splitext(os.path.basename(path))
            entry_points.append("csdms.{name}:{name}".format(name=name))

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


def load_pymt_plugins(include_old_style=False):
    plugins = OrderedDict()

    if include_old_style:
        for plugin in load_csdms_plugins():
            if not hasattr(plugins, plugin.__name__):
                plugins[plugin.__name__] = plugin

    failed = []
    for entry_point in pkg_resources.iter_entry_points(group="pymt.plugins"):
        try:
            plugin = entry_point.load()
        except Exception:
            failed.append(entry_point.name)
        else:
            plugin = bmi_factory(plugin)
            plugins[entry_point.name] = plugin

    if len(plugins) > 0:
        status("models: {0}".format(", ".join(plugins.keys())))
    else:
        status("models: (none)")
    if failed:
        error("failed to load the following models: {0}".format(", ".join(failed)))

    Plugins = namedtuple("Plugins", plugins.keys())
    return Plugins(*plugins.values())


# builtin_extensions = (
#     "pymt.ext.mappers.esmf",
#     "pymt.ext.models.heat",
#     "pymt.ext.printers.vtk",
#     "pymt.ext.printers.ugrid",
#     "pymt.ext.printers.bov",
# )


# def load_extension(extname):
#     try:
#         mod = __import__(extname, None, None, ['setup'])
#     except ImportError as err:
#         pass
