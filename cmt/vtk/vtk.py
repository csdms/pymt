#! /bin/env python
import os
import sys
import xml.dom.minidom

import numpy as np

from encoders import encode

from types import *
from xml import *

valid_encodings = ['ascii', 'base64', 'raw']
valid_formats = ['ascii', 'base64', 'raw', 'appended']

class VtkError (Exception):
    pass
class InvalidFormatError (VtkError):
    def __init__ (self, format):
        self.name = format
    def __str__ (self):
        return '%s: Invalid format' % self.name
class InvalidEncodingError (VtkError):
    def __init__ (self, encoding):
        self.name = encoding
    def __str__ (self):
        return '%s: Invalid encoder' % self.name

class VtkWriter (xml.dom.minidom.Document):

  def __init__ (self, *args, **kwargs):
    xml.dom.minidom.Document.__init__ (self)

  def assemble (self, element):
      root = element['VTKFile']
      grid = element['Grid']
      piece = element['Piece']
      for section in ['Points', 'Coordinates', 'PointData', 'Cells', 'CellData']:
          try:
              piece.appendChild (element[section])
          except KeyError:
              pass
          except EmptyElementError:
              pass
      grid.appendChild (piece)
      root.appendChild (grid)

      try:
          root.appendChild (element['AppendedData'])
      except KeyError:
          pass

      return root

  def write (self, path, format='ascii', encoding='ascii'):
      if format not in valid_formats:
          raise InvalidFormatError (format)
      if encoding not in valid_encodings:
          raise InvalidEncodingError (encoding)

      if format=='ascii':
          encoding = 'ascii'

      self.unlink ()
      self.appendChild (self.assemble (self.get_elements (format=format, encoding=encoding)))
      self.to_xml (path)

  def to_xml (self, path):
      file = open (path, 'w')
      file.write (self.toprettyxml ())
      file.close ()

class VTKDatabase (VtkWriter):
    def write (self, path, **kwargs):
        (base, file) = os.path.split (path)
        (root, ext) = os.path.splitext (file)

        try:
            next_file = '%s_%04d%s' % (root, self._count, ext)
        except NameError:
            self._count = 0
            next_file = '%s_%04d%s' % (root, self._count, ext)

        VtkWriter.write (self, os.path.join (base, next_file), **kwargs)

        self._count += 1

if __name__ == "__main__":
    import doctest
    doctest.testmod()

