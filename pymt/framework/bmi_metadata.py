#! /usr/bin/env python
"""Incorporate CSDMS Model Metadata into PyMT.

PyMT uses the CSDMS model_metadata package, to
incorporate CSDMS Model Metadata into
BMI-enabled components when they are imported
into PyMT.  This ensures that:

*  Idenitying model information stays with the
   component as it appears within the CSDMS
   Modeling Framework. This ensures that the
   original author of the model is given
   appropriate credit and not forgotten in the
   wrapping of their model. In addition,
   a citation(s) is clearly displayed for the
   model. This ensures that a user
   running the model, either through PyMT or
   otherwise, will properly cite the original
   work that describes to model when publishing
   results that use the model.
*  Model input parameters are properly validated
   and model input files are properly constructed
   when preparing a model simulation.
"""

import os
import sys
import warnings
import re
import fnmatch
from collections import namedtuple
import types
import pkg_resources

import six
import yaml

from model_metadata import ModelMetadata

from ..babel import query_config_var, BabelConfigError


class MetadataNotFoundError(Exception):
    def __init__(self, path_to_metadata):
        self._path = path_to_metadata

    def __str__(self):
        return self._path


def bmi_data_dir(name):
    """Get a component's data dir.

    Parameters
    ----------
    name : str
        The name of the component.

    Returns
    -------
    str
        The absolute path to the data directory for the component.
    """
    try:
        datarootdir = query_config_var("datarootdir")
    except BabelConfigError:
        datarootdir = os.path.join(sys.prefix, "share")
    return os.path.join(datarootdir, "csdms", name)


def find_model_metadata(plugin):
    """Find the path to a plugin's metadata.

    Parameters
    ----------
    plugin : PyMT plugin
        A PyMT plugin object.

    Returns
    -------
    str
        Path to the folder that contains the plugin's metadata.
    """
    try:
        model_metadata_dir = plugin.METADATA
    except AttributeError:
        if isinstance(plugin, six.string_types):
            plugin_name = plugin
        else:
            try:
                plugin_name = plugin.__name__
            except AttributeError:
                plugin_name = plugin.__class__.__name__.split(".")[-1]

        path_to_mmd = bmi_data_dir(plugin_name)
    else:
        path_to_mmd = pkg_resources.resource_filename(
            plugin.__module__, model_metadata_dir
        )

    return path_to_mmd


class PluginMetadata(ModelMetadata):
    def __init__(self, model):
        path_to_mmd = find_model_metadata(model)

        ModelMetadata.__init__(self, path_to_mmd)
