#! /usr/bin/env python
import os
import urllib
import zipfile
import tempfile
import shutil
import string

import yaml

from ..utils.run_dir import cd
from .bmi_metadata import bmi_data_dir, load_bmi_metadata


def update_values(values, defaults):
    if not set(values.keys()).issubset(defaults.keys()):
        raise ValueError('Unknown values')

    updated = defaults.copy()
    updated.update(values)
    return updated


class SafeFormatter(string.Formatter):
    def get_field(self, field_name, args, kwargs):
        try:
            val = super(SafeFormatter, self).get_field(field_name, args,
                                                       kwargs)
        except (KeyError, AttributeError):
            val = '{' + field_name + '}', field_name 

        return val 

    def format_field(self, value, spec):
        try:
            return super(SafeFormatter, self).format_field(value, spec)
        except ValueError:
            return value


def sub_parameters(string, **kwds):
    formatter = SafeFormatter()
    return formatter.format(string, **kwds)


class SetupMixIn(object):
    def __init__(self):
        name = self.__class__.__name__.split('.')[-1]

        self._datadir = bmi_data_dir(name)
        meta = load_bmi_metadata(name)

        self._defaults = {}
        self._parameters = {}
        for name, param in meta['defaults'].items():
            self._parameters[name] = param.value
            self._defaults[name] = param.value, param.units

    def setup(self, *args, **kwds):
        if len(args) == 0:
            dir = tempfile.mkdtemp()
        else:
            dir = args[0]

        self._parameters.update(kwds)

        files = []
        for file_ in os.listdir(self.datadir):
            if file_ not in ('api.yaml', 'parameters.yaml', 'info.yaml'):
                files.append(os.path.join(self.datadir, file_))

        with cd(dir, create=True):
            for file_ in files:
                (base, ext) = os.path.splitext(file_)
                if ext == '.tmpl':
                    with open(file_, 'r') as fp:
                        template = fp.read()
                    (_, name) = os.path.split(base)
                    with open(name, 'w') as fp:
                        fp.write(sub_parameters(template, **self._parameters))
                        # fp.write(template.format(**self._parameters))
                else:
                    shutil.copy(file_, '.')

        return dir

    @property
    def parameters(self):
        return self._parameters.items()

    @property
    def defaults(self):
        return self._defaults.items()

    @property
    def datadir(self):
        return self._datadir

    # @property
    # def author(self):
    #     try:
    #         return '{author} <{email}>'.format(**self._info)
    #     except KeyError:
    #         return self._info.get('author', 'unknown')

    # @property
    # def url(self):
    #     return self._info.get('url', 'unknown')

    # @property
    # def license(self):
    #     return self._info.get('license', 'unknown')

    # @property
    # def doi(self):
    #     return self._info.get('doi', 'unknown')

    # @property
    # def version(self):
    #     return self._info.get('version', 'unknown')

    # @property
    # def summary(self):
    #     return self._info.get('summary', '')


class GitHubSetupMixIn(object):
    def setup(self, case='default', name=None, path=None):
        if name is None:
            try:
                name = self.name
            except AttributeError:
                name = self.get_component_name()
        input_dir = fetch_input(name, path=path)

        case_dir = os.path.join(input_dir, case)

        return get_initialize_arg(case_dir)


def get_initialize_arg(dir):
    """Get the BMI initialize argument for a set of input files.

    Parameters
    ----------
    dir : str
        Path to a folder that contains input files.

    Returns
    -------
    str
        Argument that can be passed to a BMI initialize method.
    """
    readme = os.path.join(dir, 'README.yaml')
    with open(readme, 'r') as fp:
        metadata = yaml.load(fp)

    args = metadata['bmi']['initialize']['args']
    if isinstance(args, dict):
        with tempfile.NamedTemporaryFile('w', dir=dir, delete=False) as fp:
                fp.write(args['contents'])
                args = fp.name
    return args


def url_to_input_file_repo(name):
    """URL to a repo of input files for a component.

    Parameters
    ----------
    name : str
        Component name.

    Returns
    -------
    str
        URL of input-file repository.
    """
    return 'https://github.com/mcflugen/{name}-input'.format(name=name)


def url_to_input_file_zip(name):
    """URL of zip file on input files.

    Parameters
    ----------
    name : str
        Component name.

    Returns
    -------
    str
        URL of zip file of input files.
    """
    return os.path.join(url_to_input_file_repo(name), 'archive', 'master.zip')


def fetch_input(name, path=None):
    """Fetch input for a BMI component.

    Parameters
    ----------
    name : str
        Component name.
    path : str, optional
        Directory to extract into.

    Returns
    -------
    str
        Path to input files for various cases.
    """
    extract_to = os.path.abspath(path or tempfile.mkdtemp())

    (path_, _) = urllib.urlretrieve(url_to_input_file_zip(name))

    with zipfile.ZipFile(path_, 'r') as zipfp:
        zipfp.extractall(path=extract_to)

    return os.path.join(extract_to, '{name}-input-master'.format(name=name))
