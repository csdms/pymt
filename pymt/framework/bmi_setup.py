#! /usr/bin/env python
import os
import errno
import urllib
import zipfile
import tempfile
import shutil
import string

import yaml

from .bmi_metadata import PluginMetadata
from model_metadata.model_setup import FileSystemLoader
from model_metadata.model_data_files import FileTemplate
from scripting.contexts import cd


class SetupMixIn(object):
    def __init__(self):
        name = self.__class__.__name__.split('.')[-1]

        self._meta = PluginMetadata(self)

        self._defaults = {}
        self._parameters = {}
        for name, param in self._meta.parameters.items():
            self._parameters[name] = param['value']['default']
            try:
                units = param['units']
            except KeyError:
                units = None
            self._defaults[name] = param['value'], units

    def setup(self, *args, **kwds):
        """Set up a simulation.

        Parameters
        ----------
        path : str, optional
            Path to a folder to set up the simulation. If not given,
            use a temporary folder.

        Returns
        -------
        str
            Path to the folder that contains the set up simulation.
        """
        if len(args) == 0:
            dir = tempfile.mkdtemp()
        else:
            dir = args[0]

        self._parameters.update(kwds)

        FileSystemLoader(self.datadir).stage_all(dir, **self._parameters)

        config = self._meta.run['config_file']
        if config['contents'] and not config['path']:
            config['path'] = dir

        if config['path']:
            with cd(dir):
                config_file = FileTemplate.write(config['contents'],
                                                 config['path'],
                                                 **self._parameters)
        else:
            config_file = None

        return config_file, os.path.abspath(dir)

    @property
    def parameters(self):
        return self._parameters.items()

    @property
    def defaults(self):
        return self._defaults.items()

    @property
    def datadir(self):
        return self._meta.base

    @property
    def author(self):
        return self._meta.info['author']

    @property
    def email(self):
        return self._meta.info['email']

    @property
    def contact(self):
        contact = self.author
        email = self.email
        if email != '-':
            contact = '{name} <{email}>'.format(name=contact, email=email)
        return contact

    @property
    def url(self):
        return self._meta.info['url']

    @property
    def license(self):
        return self._meta.info['license']

    @property
    def doi(self):
        return self._meta.info['doi']

    @property
    def version(self):
        return self._meta.info['version']

    @property
    def summary(self):
        return self._meta.info['summary']

    @property
    def cite_as(self):
        return self._meta.info['cite_as']


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
