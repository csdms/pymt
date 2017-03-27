#! /usr/bin/env python
import os
import textwrap

import jinja2

from .bmi_metadata import load_bmi_metadata


_DOCSTRING = u"""
Basic Model Interface for {name}.

{{desc}}

author: {{author}}
version: {{version}}
license: {{license}}
DOI: {{doi}}
URL: {{url}}
{% if parameters %}
Parameters
----------
{% for param in parameters -%}
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
    
    params = meta['defaults'].values()
    params.sort(key=lambda p: p.name)

    env = jinja2.Environment(loader=jinja2.DictLoader({'docstring': _DOCSTRING}))
    return env.get_template('docstring').render(
        desc=desc, name=name,
        parameters=params,
        author=meta['info'].author,
        version=meta['info'].version,
        license=meta['info'].license,
        doi=meta['info'].doi,
        url=meta['info'].url,
    )
