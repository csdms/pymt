#! /usr/bin/env python


import os
from collections import defaultdict


from cmt.templatefiles.template_file import TemplateFile


class TemplateFileCollection(object):
    def __init__ (self, files=[]):
        self._files = defaultdict(list)
        self.add_files(files)

    @property
    def sources(self):
        return set(self._files.keys())

    @property
    def destinations(self):
        destinations = []
        for templates in self._files.values():
            for template in templates:
                destinations.append(template.destination)
        return destinations

    def add_file(self, source, **kwds):
        self._files[source].append(TemplateFile(source, **kwds))

    def add_files(self, files):
        for (src, dest) in files:
            self.add_file(src, destination=dest)

    def substitute(self, mapping, todir='.', interpolate=True):
        for (source, templates) in self._files.items():
            for template in templates:
                path_to_dest = os.path.join(todir, template.destination)
                template.tofile(mapping, file=path_to_dest,
                                interpolate=interpolate)

