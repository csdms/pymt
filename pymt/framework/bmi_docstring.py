#! /usr/bin/env python
import jinja2
import six

from model_metadata import MetadataNotFoundError

from .bmi_metadata import PluginMetadata

_DOCSTRING = u"""
Basic Model Interface for {{ name }}.

{{ desc|trim|wordwrap(70) if desc }}

{% if author -%}
Author:
{%- for name in author %}
{{"- " + name|trim }}{% endfor %}
{%- endif %}
Version: {{ version }}
License: {{ license }}
DOI: {{ doi }}
URL: {{ url }}

{% if cite_as -%}
Cite as:
{% for citation in cite_as %}
{{ citation|trim|indent(width=4, indentfirst=True) }}
{% endfor %}
{%- endif %}
{% if parameters %}
Parameters
----------
{% for param in parameters|sort(attribute='name') -%}
{{param.name}} : {{param.value.type}}, optional
    {{ "%s [default=%s %s]"|format(param.description, param.value.default, param.value.units)|trim|wordwrap(70)|indent(4) }}
{% endfor %}
{% endif -%}

Examples
--------
>>> from pymt.models import {{name}}
>>> model = {{name}}()
>>> (fname, initdir) = model.setup()
>>> model.initialize(fname, dir=initdir)
>>> for _ in xrange(10):
...     model.update()
>>> model.finalize()
""".strip()


def bmi_docstring(
    plugin,
    author=None,
    version=None,
    license=None,
    doi=None,
    url=None,
    parameters=None,
    summary=None,
    cite_as=None,
    email=None,
):
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
    cite_as : iterable of str, optional
        List of citations for this component.
    email : str, optional
        Contact email address.

    Returns
    -------
    str
        The docstring.

    Examples
    --------
    >>> from __future__ import print_function
    >>> from pymt.framework.bmi_docstring import bmi_docstring
    >>> print(bmi_docstring('Model', author='Walt Disney')) #doctest: +ELLIPSIS
    Basic Model Interface for Model.
    ...
    """
    author = author or []
    cite_as = cite_as or []

    try:
        meta = PluginMetadata(plugin)
    except MetadataNotFoundError:
        if isinstance(plugin, six.string_types):
            info = dict(
                authors=author,
                version=version,
                license=license, # pylint: disable=redefined-builtin
                doi=doi,
                url=url,
                summary=summary,
                cite_as=cite_as,
            )
            defaults = {}
            name = plugin
        else:
            raise
    else:
        info = meta.info
        defaults = meta.parameters
        name = meta.name

    for param_name, param in defaults.items():
        param["name"] = param_name
    defaults = defaults.values()

    author = author or info["authors"]
    email = email or "-"
    version = version or info["version"]
    license = license or info["license"]
    doi = doi or info["doi"]
    url = url or info["url"]
    summary = summary or info["summary"]
    cite_as = cite_as or info["cite_as"]
    parameters = parameters or defaults

    if isinstance(author, six.string_types):
        author = [author]
    if isinstance(cite_as, six.string_types):
        cite_as = [cite_as]

    env = jinja2.Environment(loader=jinja2.DictLoader({"docstring": _DOCSTRING}))
    return env.get_template("docstring").render(
        desc=summary,
        name=name,
        parameters=parameters,
        author=author,
        version=version,
        license=license,
        doi=doi,
        url=url,
        cite_as=cite_as,
    )
