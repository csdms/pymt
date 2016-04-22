#! /usr/bin/env python
import os
import errno
import urllib
import zipfile
import tempfile
import shutil

import yaml

from ..utils.run_dir import cd
from .bmi_metadata import bmi_data_dir, load_bmi_metadata


def mkdir_p(path):
    """Make a directory along with any parents."""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def update_values(values, defaults):
    if not set(values.keys()).issubset(defaults.keys()):
        raise ValueError('Unknown values')

    updated = defaults.copy()
    updated.update(values)
    return updated


def find_bmi_data_files(datadir):
    """Look for BMI data files.
    
    Parameters
    ----------
    datadir : str
        Path the the BMI component's data directory.

    Returns
    -------
    list of str
        List of the data files relative to their data directory.
    """
    fnames = []
    for dir, _, files in os.walk(datadir):
        fnames += [os.path.join(dir, fname) for fname in files]
    end_prefix = len(os.path.commonprefix(fnames))

    fnames = [fname[end_prefix:] for fname in fnames]
    for fname in ('api.yaml', 'parameters.yaml', 'info.yaml'):
        try:
            fnames.remove(fname)
        except ValueError:
            pass

    return fnames


def fill_template_file(src, dest, **kwds):
    """Substitute values into a template file.

    Parameters
    ----------
    src : str
        Path to a template file.
    dest : str
        Path to output file that will contain the substitutions.
    """
    (srcdir, fname) = os.path.split(src)
    dest = os.path.abspath(dest)

    with cd(srcdir):
        with open(fname, 'r') as fp:
            template = fp.read()

        (base, ext) = os.path.splitext(dest)
        if ext == '.tmpl':
            dest = base
        else:
            dest = fname

        with open(dest, 'w') as fp:
            fp.write(template.format(**kwds))


def copy_data_files(datadir, destdir, **kwds):
    """Copy BMI data files into a folder, filling template files on the way.

    Parameters
    ----------
    datadir : str
        Path to the BMI component's data folder.
    destdir : str
        Path to the folder to copy the data into.
    """
    files = find_bmi_data_files(datadir)

    with cd(destdir, create=True):
        for dest in files:
            src = os.path.join(datadir, dest)

            mkdir_p(os.path.dirname(dest))

            if src.endswith('.tmpl'):
                fill_template_file(src, dest, **kwds)
            else:
                shutil.copy2(src, dest)


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

        copy_data_files(self.datadir, dir, **self._parameters)
        
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
