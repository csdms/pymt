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
import model_metadata
from model_metadata import ModelMetadata


class MetadataNotFoundError(Exception):
    def __init__(self, path_to_metadata):
        self._path = path_to_metadata

    def __str__(self):
        return self._path


class PluginMetadata(ModelMetadata):
    def __init__(self, model):
        path_to_mmd = model_metadata.api.find(model)

        ModelMetadata.__init__(self, path_to_mmd)
