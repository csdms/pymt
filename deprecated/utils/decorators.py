#! /usr/bin/env python
import os
import textwrap
import warnings
from functools import wraps


class cache_result_in_object(object):
    def __init__(self, cache_as=None):
        self._attr = cache_as

    def __call__(self, func):
        name = self._attr or "_" + func.__name__

        @wraps(func)
        def _wrapped(obj):
            if not hasattr(obj, name):
                setattr(obj, name, func(obj))
            return getattr(obj, name)

        return _wrapped


class deprecated(object):

    """Mark a function as deprecated."""

    def __init__(self, use=None):
        self._use = use

    def __call__(self, func):
        doc_lines = (func.__doc__ or "").split(os.linesep)

        for lineno, line in enumerate(doc_lines):
            if len(line.rstrip()) == 0:
                break

        head = doc_lines[:lineno]
        body = doc_lines[lineno:]

        head = textwrap.dedent(os.linesep.join(head))
        body = textwrap.dedent(os.linesep.join(body))

        doc_lines = [head, ".. note:: deprecated", ""]
        if self._use is not None:
            doc_lines.extend(
                ["    Use :func:`{use}` instead.".format(use=self._use), ""]
            )
        doc_lines.append(body)

        func.__doc__ = os.linesep.join(doc_lines)

        @wraps(func)
        def _wrapped(*args, **kwargs):
            if func.__name__.startswith("_"):
                pass
            else:
                warnings.warn(
                    message="Call to deprecated function {name}.".format(
                        name=func.__name__
                    )
                )
                # category=DeprecationWarning)
            return func(*args, **kwargs)

        return _wrapped
