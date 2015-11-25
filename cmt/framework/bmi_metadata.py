#! /usr/bin/env python
import os
import warnings
from collections import namedtuple

import yaml

from ..babel import query_config_var


Parameter = namedtuple('Parameter', ('name', 'value', 'units', 'desc'))
ModelInfo = namedtuple('ModelInfo', ('name', 'author', 'version', 'license',
                                     'doi', 'url', 'summary'))


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
    datarootdir = query_config_var('datarootdir')
    return os.path.join(datarootdir, 'csdms', name)


def load_model_info(path):
    """Load model info from a BMI metadata file.

    Parameters
    ----------
    path : str
        Path to the folder that contains BMI metadata files.

    Returns
    -------
    ModelInfo
        A namedtuple that contains the model metadata.
    """
    meta_yaml = os.path.join(path, 'info.yaml')
    with open(meta_yaml, 'r') as fp:
        info = yaml.load(fp.read())

    api_yaml = os.path.join(path, 'api.yaml')
    with open(api_yaml, 'r') as fp:
        api = yaml.load(fp.read())

    return ModelInfo(
        name=api['name'],
        author=info.get('author', '-'),
        version=info.get('version', '-'),
        license=info.get('license', 'None'),
        doi=info.get('doi', 'None'),
        url=info.get('url', 'None'),
        summary=info.get('summary', ''),
    )


def load_default_parameters(path):
    """Load model default paramters from a BMI metadata file.

    Parameters
    ----------
    path : str
        Path to the folder that contains BMI metadata files.

    Returns
    -------
    dict
        A dictionary of parameter names as keys and namedtuple as values that
        contains a description of the parameter.
    """
    params_yaml = os.path.join(path, 'parameters.yaml')
    with open(params_yaml, 'r') as fp:
        param_groups = yaml.load_all(fp.read())

    p = {}
    for group in param_groups:
        for name, param in group.items():
            if not name.startswith('_'):
                value = param['value']['default']
                try:
                    units = param['value']['units']
                except KeyError:
                    units = '-'
                    warnings.warn('missing units for {name}'.format(name=name))
                p[name] = Parameter(name=name, value=value, units=units,
                                    desc=param['description'])
    return p



def load_bmi_metadata(name):
    """Load all BMI metadata for a component.

    Parameters
    ----------
    name : str
        Name of a CSDMS component.

    Returns
    -------
    dict
        A dictionary of the BMI metadata. There are two keys, 'defaults'
        for the default parameters and 'info' model metadata.
    """
    meta = dict()

    datadir = bmi_data_dir(name)
    meta['defaults'] = load_default_parameters(datadir)
    meta['info'] = load_model_info(datadir)

    parameters = dict()
    for name, param in meta['defaults'].items():
        parameters[name] = param.value, param.units
    meta['parameters'] = parameters

    return meta
