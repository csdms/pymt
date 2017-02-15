#! /usr/bin/env python
import os
import warnings
import re
import fnmatch
from collections import namedtuple
import types

import yaml

from ..babel import query_config_var


Parameter = namedtuple('Parameter', ('name', 'value', 'units', 'desc', 'type'))
ModelInfo = namedtuple('ModelInfo', ('name', 'author', 'version', 'license',
                                     'doi', 'url', 'summary'))
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
    datarootdir = query_config_var('datarootdir')
    return os.path.join(datarootdir, 'csdms', name)


def bmi_data_files(path):
    files = []
    for file_ in os.listdir(path):
        if file_ not in ('api.yaml', 'parameters.yaml', 'info.yaml', 'run.yaml'):
            files.append(os.path.join(path, file_))

    return files


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


def load_run_section(path):
    run_yaml = os.path.join(path, 'run.yaml')
    if os.path.isfile(run_yaml):
        with open(run_yaml, 'r') as fp:
            run = yaml.load(fp.read())
    else:
        run = {}

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
    meta['info'] = load_model_info(datadir)
    meta['run'] = load_run_section(datadir)

    parameters = dict()
    for name, param in meta['defaults'].items():
        parameters[name] = param.value, param.units
    meta['parameters'] = parameters

    return meta
