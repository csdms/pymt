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

import yaml

from model_metadata import ModelMetadata

from ..babel import query_config_var, BabelConfigError



Parameter = namedtuple('Parameter', ('name', 'value', 'units', 'desc', 'type'))
ModelInfo = namedtuple('ModelInfo', ('name', 'author', 'email', 'version',
                                     'license', 'doi', 'url', 'summary',
                                     'cite_as'))
ModelRun = namedtuple('ModelRun', ('config_file', ))
ParameterSection = namedtuple('ParameterSection', ('title', 'members'))


def expand_members(members, params):
    """Get all members from a larger set.

    Parameters
    ----------
    members : str
        Glob-stype pattern to match members from the group.
    params : iterable of str
        List of all members.

    Returns
    -------
    list of str
        List of all matching members.
    """
    p = re.compile(fnmatch.translate(members))
    expanded = filter(p.match, params)
    if len(expanded) == 0:
        warnings.warn(
            'group contains no members ({glob})'.format(glob=members))
    return expanded


def load_parameter_groups(path):
    """Load groups of parameters from a file.

    Parameters
    ----------
    path : str
        Path to folder that contains metadata.

    Returns
    -------
    dict
        Parameter groups as a dictionary of group name and a list of members.
    """
    params = load_default_parameters(path)

    with open(os.path.join(path, 'wmt.yaml'), 'r') as fp:
        obj = yaml.load(fp)

    groups = dict()
    for group in obj['groups']:
        name, members = None, group

        if isinstance(group, dict):
            name, members = group.items()[0]
        elif isinstance(group, types.StringTypes):
            members = group

        if isinstance(members, types.StringTypes):
            members = expand_members(members, params)
        if name is None:
            name = os.path.commonprefix(members)

        if name in groups:
            warnings.warn(
                'overwriting already-existing group (name).'.format(name=name))
        groups[name] = members

    return groups


def load_parameter_sections(path):
    """Load a parameter section description from a file.

    Parameters
    ----------
    path : str
        Path to folder that contains metadata.

    Returns
    -------
    list of ParameterSection
        The sections.
    """
    params = load_default_parameters(path)

    with open(os.path.join(path, 'wmt.yaml'), 'r') as fp:
        obj = yaml.load(fp)

    groups = load_parameter_groups(path)

    sections = []
    for section in obj['sections']:
        title, members = section['title'], section['members']
        if isinstance(members, types.StringTypes):
            try:
                members = groups[members]
            except KeyError:
                members = expand_members(members, params)

        if not isinstance(members, list):
            warnings.warn('bad type for section')

        all = []
        for member in members:
            if member in params:
                member = [member]
            elif member in groups:
                member = groups[member]
            else:
                member = expand_members(member, params)
            all.extend(member)

        sections.append(ParameterSection(title, all))

    return sections


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
        datarootdir = query_config_var('datarootdir')
    except BabelConfigError:
        datarootdir = os.path.join(sys.prefix, 'share')
    return os.path.join(datarootdir, 'csdms', name)


def bmi_data_files(path):
    files = []
    for file_ in os.listdir(path):
        if file_ not in ('api.yaml', 'parameters.yaml', 'info.yaml', 'run.yaml'):
            files.append(os.path.join(path, file_))

    return files


def load_meta_section(path, section):
    meta_path = os.path.join(path, 'meta.yaml')
    if os.path.isfile(meta_path):
        with open(meta_path, 'r') as fp:
            meta = yaml.load(fp.read())
    else:
        meta = {}

    try:
        meta_section = meta[section]
    except KeyError:
        section_path = os.path.join(path, '{section}.yaml'.format(section=section))
        try:
            with open(section_path, 'r') as fp:
                meta_section = yaml.load(fp.read())
        except IOError:
            meta_section = {}

    return meta_section


def load_names_section(path):
    return load_meta_section(path, 'names')


def load_info_section(path):
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
    info = load_meta_section(path, 'info')
    api = load_meta_section(path, 'api')

    info.setdefault('cite_as', [])
    if isinstance(info['cite_as'], types.StringTypes):
        info['cite_as'] = [info['cite_as']]
    author = info.get('author', ['anonymous'])
    if isinstance(author, types.StringTypes):
        author = [author]

    return ModelInfo(
        name=api['name'],
        author=author,
        email=info.get('email', '-'),
        version=info.get('version', '-'),
        license=info.get('license', 'None'),
        doi=info.get('doi', 'None'),
        url=info.get('url', 'None'),
        summary=info.get('summary', ''),
        cite_as=info['cite_as'],
    )


def load_run_section(path):
    run = load_meta_section(path, 'run')

    return ModelRun(
        config_file=run.get('config_file', ''),
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

    # param_groups = load_meta_section(path, 'parameters')

    p = {}
    for group in param_groups:
        for name, param in group.items():
            if name.startswith('_'):
                continue
            try:
                value = param['value']['default']
            except TypeError:
                print name, param, path
                raise
            try:
                units = param['value']['units']
            except KeyError:
                units = '-'
                # warnings.warn('missing units for {name}'.format(
                #     name=name))

            type = param['value']['type']
            if type == 'choice':
                choices = [repr(choice) for choice in param['value']['choices']]
                type = '{' + ', '.join(choices) + '}'
            elif type == 'file':
                type = 'str'

            p[name] = Parameter(name=name, value=value, units=units,
                                desc=param['description'], type=type)
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
        for the default parameters and 'info' for model metadata.
    """
    meta = dict()

    datadir = bmi_data_dir(name)
    meta['defaults'] = load_default_parameters(datadir)
    meta['info'] = load_info_section(datadir)
    meta['run'] = load_run_section(datadir)
    meta['names'] = load_names_section(datadir)

    parameters = dict()
    for name, param in meta['defaults'].items():
        parameters[name] = param.value, param.units
    meta['parameters'] = parameters

    return meta


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
        path_to_mmd = bmi_data_dir(plugin.__name__)
    else:
        path_to_mmd = pkg_resources.resource_filename(plugin.__module__,
                                                      model_metadata_dir)

    return path_to_mmd


class PluginMetadata(ModelMetadata):

    def __init__(self, model):
        path_to_mmd = find_model_metadata(model)

        ModelMetadata.__init__(self, path_to_mmd)
