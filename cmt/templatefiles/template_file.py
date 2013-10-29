#! /usr/bin/env python

import os
import sys
import types
from string import Template


class Error(Exception):
    pass


class FileNotFoundError(Error):
    def __init__(self, filename):
        self._file = filename

    def __str_(self):
        return self._file


class FileNameError(Error):
    def __init__(self, filename):
        self._file = filename

    def __str_(self):
        return self._file


def search_paths_for_file(file, paths=['.']):
    for path in paths:
        path_to_file = os.path.join(path, file)
        if os.path.isfile(path_to_file):
            return path_to_file
    raise FileNotFoundError(file)


def user_search_paths(var_name):
    try:
        paths = os.environ[var_name]
    except KeyError:
        return ['.']
    else:
        return paths.split(os.pathsep)


def interpolate_item_inplace(key, mapping):
    if isinstance(mapping[key], types.StringTypes):
        mapping[key] = Template(mapping[key]).safe_substitute(mapping)


def interpolate_mapping_inplace(mapping):
    n_interpolations = 0
    for (key, value) in mapping.items():
        interpolate_item_inplace(key, mapping)

        if mapping[key] != value:
            n_interpolations += 1
    return n_interpolations


def interpolate_mapping(mapping, maxiter=100):
    iters = 0
    while 1:
        n_interpolations = interpolate_mapping_inplace(mapping)
        if n_interpolations == 0:
            break

        iters += 1
        if iters >= maxiter:
            break
            #raise RuntimeError(
            #    'max iterations reached in dictionary interpolation')

    return mapping


class TemplateFile(object):
    def __init__ (self, file, destination=None):
        self._template = self._template_from_file(file)
        if destination is None:
            if isinstance(file, types.StringTypes):
                self._destination = self.get_destination_file_name(file)
            else:
                try:
                    self._destination = self.get_destination_file_name(file.name)
                except AttributeError:
                    self._destination = sys.stdout
        else:
            self._destination = destination

    @property
    def template(self):
        return self._template

    @property
    def destination(self):
        return self._destination

    @staticmethod
    def _template_from_file(file):
        try:
            template = file.read()
        except AttributeError:
            try:
                path_to_file = search_paths_for_file(
                    file, user_search_paths('CMT_PROJECT_TEMPLATE_PATH'))
            except FileNotFoundError:
                raise
            else:
                with open(path_to_file, 'r') as source:
                    template = source.read()
        return Template(template)

    @staticmethod
    def get_destination_file_name(source_file):
        (root, ext) = os.path.splitext(source_file)
        if ext != '.in':
            raise FileNameError(source_file)
        return root

    def substitute(self, mapping, **kwds):
        return self.tostr(mapping, **kwds)

    def tofile(self, mapping, file=None, **kwds):
        if file is None:
            file = self._destination
        if isinstance(file, types.StringTypes):
            with open(file, 'w') as destination:
                destination.write(self.tostr(mapping, **kwds))
        else:
            file.write(self.tostr(mapping, **kwds))

    def tostr(self, mapping, interpolate=True):
        if interpolate:
            mapping = interpolate_mapping(mapping)
        return self._template.safe_substitute(mapping)
