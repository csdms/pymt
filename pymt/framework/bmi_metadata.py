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

import model_metadata
import pkg_resources
import six
from model_metadata import ModelMetadata

from ..babel import BabelConfigError, query_config_var


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


class PluginMetadata(ModelMetadata):
    def __init__(self, model):
        path_to_mmd = model_metadata.api.find(model)

        ModelMetadata.__init__(self, path_to_mmd)
