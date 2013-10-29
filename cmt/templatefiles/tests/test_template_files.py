#! /usr/bin/env python

import unittest
import os
import sys
import tempfile
from StringIO import StringIO
from collections import OrderedDict

from cmt.templatefiles.template_files import TemplateFileCollection


class TestTemplateFileCollection(unittest.TestCase):
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

    def test_init(self):
        files = TemplateFileCollection()
        self.assertSetEqual(set(), files.sources)
        self.assertListEqual([], files.destinations)

    def test_init_with_file(self):
        name = self._create_file('<empty>')
        files = TemplateFileCollection([(name, None)])
        self.assertSetEqual(set([name]), files.sources)

        (base, _) = os.path.splitext(name)
        self.assertListEqual([base], files.destinations)

    def test_init_with_files(self):
        names = [self._create_file('<empty>'),
                 self._create_file('<empty>')]

        files = TemplateFileCollection(zip(names, (None, None)))
        self.assertSetEqual(set(names), files.sources)

        dests = [os.path.splitext(name)[0] for name in names]
        self.assertSetEqual(set(dests), set(files.destinations))

    def test_add_file(self):
        name = self._create_file('var = ${value}')

        files = TemplateFileCollection()
        files.add_file(name)

        self.assertSetEqual(set([name]), files.sources)

    def test_add_files(self):
        names = (self._create_file('<empty>'),
                 self._create_file('<empty>'))

        files = TemplateFileCollection()
        files.add_files(zip(names, (None, None)))

        self.assertSetEqual(set(names), files.sources)

        dests = [os.path.splitext(name)[0] for name in names]
        self.assertSetEqual(set(dests), set(files.destinations))

    def test_multiple_destinations(self):
        name = self._create_file('<empty>')

        files = TemplateFileCollection()
        files.add_file(name, destination='file_1.txt')
        files.add_file(name, destination='file_2.txt')

        self.assertSetEqual(set([name]), files.sources)
        self.assertSetEqual(set(['file_1.txt', 'file_2.txt']),
                            set(files.destinations))

        name = self._create_file('<empty>')
        files.add_file(name, destination='file_3.txt')
        self.assertSetEqual(set(['file_1.txt', 'file_2.txt', 'file_3.txt']),
                            set(files.destinations))

    def test_substitute_one_file(self):
        source = self._create_file('var = ${value}')
        destination = self._create_file('<empty>')
        files = TemplateFileCollection([(source, destination)])
        files.substitute(dict(value='ten'))
        with open(destination, 'r') as opened_file:
            self.assertEqual('var = ten', opened_file.read())

    def test_substitute_one_to_many(self):
        source = self._create_file('var = ${value}')
        destinations = (self._create_file('<empty>'),
                        self._create_file('<empty>'))
        files = TemplateFileCollection([(source, destinations[0]),
                                        (source, destinations[1])])
        files.substitute(dict(value='ten'))
        for destination in destinations:
            with open(destination, 'r') as opened_file:
                self.assertEqual('var = ten', opened_file.read())

    def test_substitute_many_to_many(self):
        sources = (self._create_file('var = ${ten}'),
                   self._create_file('var = ${two}'))
        destinations = (self._create_file('<empty>'),
                        self._create_file('<empty>'))
        files = TemplateFileCollection(zip(sources, destinations))
        files.substitute(dict(ten='10', two='2'))

        with open(destinations[0], 'r') as opened_file:
            self.assertEqual('var = 10', opened_file.read())
        with open(destinations[1], 'r') as opened_file:
            self.assertEqual('var = 2', opened_file.read())
