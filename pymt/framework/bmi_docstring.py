#! /usr/bin/env python
import os
import textwrap

from .bmi_metadata import load_bmi_metadata


_DOCSTRING = u"""
Basic Modeling Interface for {name}.

{desc}

author: {author}
version: {version}
license: {license}
DOI: {doi}
URL: {url}

Parameters
----------
{parameters}

Examples
--------
>>> from pymt.components import {name}
>>> model = {name}()
>>> (fname, initdir) = model.setup()
>>> model.initialize(fname, dir=initdir)
>>> for _ in xrange(10):
...     model.update()
>>> model.finalize()
""".strip()


_PARAM_DECL = "{name} : {type}, optional"
_PARAM_DESC = "{desc} [default={default} {units}]."


def build_parameters_section(parameters):
    """Build the paramters section of the docstring for a BMI model.

    Parameters
    ----------
    parameters : dict
        Parameters names and descriptions.

    Returns
    -------
    str
        The paramters section.
    """
    params = parameters.values()
    params.sort(key=lambda p: p.name)

    docstrings = []
    for param in params:
        decl = _PARAM_DECL.format(name=param.name, type=param.type)
        desc = _PARAM_DESC.format(desc=param.desc, default=param.value,
                                  units=param.units)

        docstrings.extend(
            textwrap.wrap(decl, subsequent_indent=' ' * (decl.find(':') + 3)))
        docstrings.extend(
            textwrap.wrap(desc, initial_indent=' ' * 4,
                          subsequent_indent=' ' * 4))

    return os.linesep.join(docstrings)


def bmi_docstring(name):
    """Build the docstring for a BMI model.

    Parameters
    ----------
    name : str
        Name of a BMI component.

    Returns
    -------
    str
        The docstring.
    """
    meta = load_bmi_metadata(name)
    desc = '\n'.join(textwrap.wrap(meta['info'].summary))
    
    return _DOCSTRING.format(
        desc=desc, name=name,
        parameters=build_parameters_section(meta['defaults']),
        author=meta['info'].author,
        version=meta['info'].version,
        license=meta['info'].license,
        doi=meta['info'].doi,
        url=meta['info'].url,
    )
