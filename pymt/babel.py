#! /usr/bin/env python
"""Utility functions for working with babel projects."""
import os
import subprocess
import warnings
from string import Template
import shlex


class BabelConfigError(Exception):
    def __init__(self, prog):
        self._prog = prog

    def __str__(self):
        return self._prog


def prepend_env_path(var, path, sep=os.pathsep):
    """Prepend a path to an environment variable."""
    try:
        os.environ[var] = sep.join([path, os.environ[var]])
    except KeyError:
        os.environ[var] = path

    return path


def contains_identifiers(template):
    try:
        Template(template).substitute()
    except KeyError:
        return True
    else:
        return False


def recursive_substitute(template, **kwds):
    while contains_identifiers(template):
        try:
            template = Template(template).substitute(**kwds)
        except KeyError:
            break

    return template


def query_config_all(config='csdms-config'):
    try:
        contents = subprocess.check_output([config, '--dump'])
    except subprocess.CalledProcessError:
        warnings.warn('Error running the {prog} program.'.format(prog=config))
    except OSError:
        warnings.warn('Unable to run {prog} program.'.format(prog=config))

    vars = {}
    for line in shlex.split(contents):
        try:
            (key, var) = line.split('=', 1)
        except ValueError:
            pass
        else:
            vars[key] = var

    return vars


def query_config_var(var, config='csdms-config', interpolate=True):
    """Get a configuration variable from a babel project."""
    value = None

    try:
        value = subprocess.check_output([config, '--var', var]).strip()
    except subprocess.CalledProcessError:
        warnings.warn('Error running the {prog} program.'.format(prog=config))
    except OSError:
        warnings.warn('Unable to run {prog} program.'.format(prog=config))

    if value is None:
        raise BabelConfigError(config)

    if interpolate:
        vars = query_config_all(config=config)
        value = recursive_substitute(value, **vars)

    return value


def setup_babel_environ():
    """Set up environment variables to load babelized components."""
    try:
        prefix = query_config_var('PREFIX', config='csdms-config')
        ccaspec_babel_libs = query_config_var('CCASPEC_BABEL_LIBS',
                                              config='cca-spec-babel-config')
    except BabelConfigError:
        warnings.warn('Unable to configure for babel. Not loading components.')
    else:
        prepend_env_path('SIDL_DLL_PATH', os.path.join(prefix, 'share', 'cca'),
                         sep=';')
        prepend_env_path('LD_LIBRARY_PATH', ccaspec_babel_libs)
