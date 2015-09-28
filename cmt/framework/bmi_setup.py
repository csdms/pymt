#! /usr/bin/env python
import os
import urllib
import zipfile
import tempfile

import yaml


class SetupMixIn(object):
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
