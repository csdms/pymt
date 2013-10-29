#! /usr/bin/env python

import unittest
import os
import sys
import tempfile
from StringIO import StringIO
from collections import OrderedDict

from cmt.templatefiles.template_file import interpolate_mapping
from cmt.templatefiles.template_file import TemplateFile, FileNameError


class TestInterpolateMapping(unittest.TestCase):
    def test_empty_map(self):
        map = interpolate_mapping({})
        self.assertDictEqual({}, map)

    def test_no_interpolation(self):
        map = interpolate_mapping(dict(key='${val}'))
        self.assertDictEqual({'key': '${val}'}, map)

    def test_interpolation(self):
        map = interpolate_mapping(dict(key='${val}', val='value'))
        self.assertDictEqual({'key': 'value', 'val': 'value'}, map)

    def test_multiple_interpolation(self):
        map = interpolate_mapping(dict(key='${val}',
                                       val='${value}',
                                       value='two'))
        self.assertDictEqual({'key': 'two',
                              'val': 'two',
                              'value': 'two'}, map)

        map = interpolate_mapping(dict(key='${${value}}',
                                       two='three',
                                       value='two'))
        self.assertDictEqual({'key': 'three',
                              'two': 'three',
                              'value': 'two'}, map)

    def test_maxiter(self):
        map = interpolate_mapping(OrderedDict(
            [('key', '${val}'), ('val', '$value'), ('value', 'two')]),
             maxiter=1)
        self.assertDictEqual({'key': '$value',
                              'val': 'two',
                              'value': 'two'}, map)

        map = interpolate_mapping(OrderedDict(
            [('val', '$value'), ('key', '${val}'), ('value', 'two')]),
             maxiter=1)
        self.assertDictEqual({'val': 'two',
                              'key': 'two',
                              'value': 'two'}, map)

        map = interpolate_mapping(dict(key='${${value}}',
                                       two='three',
                                       value='two'), maxiter=1)
        self.assertDictEqual({'key': '${two}',
                              'two': 'three',
                              'value': 'two'}, map)

    def test_interpolation_with_int(self):
        map = interpolate_mapping(dict(key='${val}', val=2))
        self.assertDictEqual({'key': '2', 'val': 2}, map)


class TestTemplateFile(unittest.TestCase):
    def setUp(self):
        self._files_for_removal = set()

    def tearDown(self):
        for file in self._files_for_removal:
            try:
                os.remove(file)
            except OSError:
                pass

    def _create_file(self, contents, suffix='.in'):
        (fd, name) = tempfile.mkstemp(suffix=suffix, dir='.', text=True)
        with os.fdopen(fd, 'w') as infile:
            infile.write(contents)
        self._files_for_removal.add(name)
        return name

    def test_init_with_file_like(self):
        file = TemplateFile(StringIO("var = ${value}"))
        self.assertEqual("var = two", file.substitute(dict(value='two')))

    def test_init_with_file_name(self):
        name = self._create_file('var = ${value}')

        file = TemplateFile(name)
        self.assertEqual("var = two", file.substitute(dict(value='two')))

    def test_init_with_opened_file(self):
        name = self._create_file('var = ${value}')

        with open(name, 'r') as infile:
            file = TemplateFile(name)
        self.assertEqual("var = two", file.substitute(dict(value='two')))

    def test_destination_with_file_like(self):
        file = TemplateFile(StringIO("var = ${value}"))
        self.assertEqual(sys.stdout, file.destination)

    def test_destination_with_file_name(self):
        name = self._create_file('')
        file = TemplateFile(name)
        (expected_name, _) = os.path.splitext(name)
        self.assertEqual(expected_name, file.destination)

    def test_destination_with_opened_file(self):
        name = self._create_file('var = ${value}')

        with open(name, 'r') as infile:
            file = TemplateFile(infile)
            (expected_name, _) = os.path.splitext(name)
            self.assertEqual(expected_name, file.destination)

    def test_init_with_bad_file_name(self):
        name = self._create_file('var = ${value}', suffix='.txt')
        with self.assertRaises(FileNameError):
            TemplateFile(name)

    def test_init_with_destination_name(self):
        name = self._create_file('var = ${value}', suffix='.txt')
        destination_name = self._create_file('', suffix='.out')
        file = TemplateFile(name, destination=destination_name)
        self.assertEqual(destination_name, file.destination)

    def test_clobber_named_destination(self):
        name = self._create_file('var = ${value}', suffix='.txt')
        destination_name = self._create_file('some text', suffix='.out')
        file = TemplateFile(name, destination=destination_name)
        file.tofile(dict(value='two'))

        with open(destination_name, 'r') as opened_file:
            self.assertEqual("var = two", opened_file.read())

    def test_clobber_opened_destination(self):
        name = self._create_file('var = ${value}', suffix='.txt')
        destination_name = self._create_file('some text', suffix='.out')

        with open(destination_name, 'w') as opened_destination:
            file = TemplateFile(name, destination=opened_destination)
            file.tofile(dict(value='two'))

        with open(destination_name, 'r') as opened_file:
            self.assertEqual("var = two", opened_file.read())

    def test_with_interpolation(self):
        name = self._create_file("var = ${value}")
        file = TemplateFile(name)

        self.assertEqual("var = three", file.substitute(
            dict(value='${another_value}', another_value='three')))
