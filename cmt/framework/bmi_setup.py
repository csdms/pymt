#! /usr/bin/env python
import os
import urllib
import zipfile
import tempfile
import warnings
import shutil

import yaml

from ..babel import query_config_var
from ..utils.run_dir import cd


def load_default_parameters(path):
    with open(path, 'r') as fp:
        param_groups = yaml.load_all(fp.read())

    p = {}
    for group in param_groups:
        for name, param in group.items():
            if not name.startswith('_'):
                p[name] = param['value']['default']
    return p


def load_info(path):
    with open(path, 'r') as fp:
        info = yaml.load(fp.read())
    return info


def update_values(values, defaults):
    if not set(values.keys()).issubset(defaults.keys()):
        raise ValueError('Unknown values')

    updated = defaults.copy()
    updated.update(values)
    return updated


class SetupMixIn(object):
    def __init__(self):
        datarootdir = query_config_var('datarootdir')
        name = self.__class__.__name__.split('.')[-1]
        self._datadir = os.path.join(datarootdir, 'csdms', name)
        self._defaults = load_default_parameters(
            os.path.join(self.datadir, 'parameters.yaml')) 
        self._info = load_info(os.path.join(self.datadir, 'info.yaml'))

    def setup(self, dir=None, values=None):
        if values is None:
            values = dict(self.defaults)
        else:
            values = update_values(values, self._defaults)

        dir = dir or tempfile.mkdtemp()

        files = []
        for file_ in os.listdir(self.datadir):
            if file_ not in ('api.yaml', 'parameters.yaml', 'info.yaml'):
                files.append(os.path.join(self.datadir, file_))

        with cd(dir):
            for file_ in files:
                (base, ext) = os.path.splitext(file_)
                if ext == '.tmpl':
                    with open(file_, 'r') as fp:
                        template = fp.read()
                    (_, name) = os.path.split(base)
                    with open(name, 'w') as fp:
                        fp.write(template.format(**values))
                else:
                    shutil.copy(file_, '.')

        return dir

    @property
    def defaults(self):
        return self._defaults.items()

    @property
    def datadir(self):
        return self._datadir

    @property
    def author(self):
        try:
            return '{author} <{email}>'.format(**self._info)
        except KeyError:
            return self._info.get('author', 'unknown')

    @property
    def url(self):
        return self._info.get('url', 'unknown')

    @property
    def license(self):
        return self._info.get('license', 'unknown')

    @property
    def doi(self):
        return self._info.get('doi', 'unknown')

    @property
    def version(self):
        return self._info.get('version', 'unknown')

    @property
    def summary(self):
        return self._info.get('summary', '')


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
