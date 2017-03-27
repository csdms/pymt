#! /usr/bin/env python
import os
import textwrap

import jinja2

from .bmi_metadata import load_bmi_metadata


_DOCSTRING = u"""
Basic Model Interface for {{ name }}.

{{ desc|trim|wordwrap(70) if desc }}

Author: {{ author }}
Version: {{ version }}
License: {{ license }}
DOI: {{ doi }}
URL: {{ url }}
{% if parameters %}
Parameters
----------
{% for param in parameters|sort(attribute='name') -%}
{{param.name}} : {{param.type}}, optional
    {{ "%s [default=%s %s]"|format(param.desc, param.value, param.units)|trim|wordwrap(70)|indent(4) }}
{% endfor %}
{% endif -%}

Examples
--------
>>> from pymt.components import {{name}}
>>> model = {{name}}()
>>> (fname, initdir) = model.setup()
>>> model.initialize(fname, dir=initdir)
>>> for _ in xrange(10):
...     model.update()
>>> model.finalize()
""".strip()


def bmi_docstring(name, author=None, version=None, license=None, doi=None,
                  url=None, parameters=None, summary=None):
    """Build the docstring for a BMI model.

    Parameters
    ----------
    name : str
        Name of a BMI component.
    author : str, optional
        Name of author or authors.
    version : str, optional
        Version string for the component.
    license : str, optional
        Name of the license of the component.
    doi : str, optional
        A DOI for the component.
    url : str, optional
        URL of the component's location on the internet.
    parameters : iterable, optional
        List of input parameters for the component. Each parameter object
        must have attributes for name, type, value, units, and desc.

    Returns
    -------
    str
        The docstring.
    """
    meta = load_bmi_metadata(name)

    author = author or meta['info'].author
    version = version or meta['info'].version
    license = license or meta['info'].license
    doi = doi or meta['info'].doi
    url = url or meta['info'].url
    summary = summary or meta['info'].summary
    parameters = parameters or meta['defaults'].values()

    env = jinja2.Environment(loader=jinja2.DictLoader({'docstring': _DOCSTRING}))
    return env.get_template('docstring').render(
        desc=summary,
        name=name,
        parameters=parameters,
        author=author,
        version=version,
        license=license,
        doi=doi,
        url=url,
    )
