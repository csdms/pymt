#! /bin/env python
"""
Examples
========

An unstructured grid
--------------------

Define a grid that consists of two trianges that share two points.

::

       (2) - (3)
      /   \  /
    (0) - (1)

Create the grid,

    >>> g = VtkUnstructuredWriter ([0, 2, 1, 3], [0, 0, 1, 1], [0, 2, 1, 2, 3, 1], [3, 6])
    >>> g.add_point_data ('Elevation', [1., 2., 3, 4])
    >>> g.add_point_data ('Temperature', [10., 20., 30., 40.])
    >>> g.add_cell_data ('Cell Elevation', [1., 2.])
    >>> g.add_cell_data ('Cell Temperature', [10., 20.])
    >>> g.write ('tri.vtu', format='appended', encoding='base64')

    >>> (x, y) = np.meshgrid ([-1., 1., 3., 5.], [-.5, .5, 1.5])
    >>> c = [0, 4, 5, 1, 1, 5, 6, 2, 2, 6, 7, 3, 4, 8, 9, 5, 5, 9, 10, 6, 6, 10, 11, 7]
    >>> o = [4, 8, 12, 16, 20, 24]
    >>> g = VtkUnstructuredWriter (x, y, c, o, encoding='base64')
    >>> g.add_point_data ('Elevation', np.arange (12.))
    >>> g.add_cell_data ('Cell Elevation', [1., 2., 3, 4, 5, 6])
    >>> g.write ('rect.vtu', format='appended', encoding='base64')

    >>> pq = PrintQueue (g)
    >>> pq.push ('Elevation')
    >>> pq.push ('Cell Elevation')

    >>> pq.print ()

"""
import os

import numpy as np

#from cmt.grid import VTKGrid
from cmt.grids import GridField
from cmt.vtk import VtkWriter

from vtktypes import VtkUnstructured, edge_count_to_type, VtkPolygon
from vtkxml import *

#class VtkUnstructuredWriter (VTKGrid, VtkWriter):
class VtkUnstructuredWriter (GridField, VtkWriter):
  _vtk_grid_type = VtkUnstructured

  def __init__ (self, *args, **kwargs):
      super (VtkUnstructuredWriter, self).__init__ (*args)
      VtkWriter.__init__ (self)

      self._types = self.get_types ()

  def get_elements (self, format='ascii', encoding='ascii'):
      if format == 'appended':
          data = VtkAppendedDataElement ('', encoding=encoding)
      else:
          data = None

      element = {}
      element ['VTKFile'] = VtkRootElement ('UnstructuredGrid')
      element ['Grid'] = VtkGridElement ('UnstructuredGrid')
      element ['Piece'] = VtkPieceElement (NumberOfPoints=self.get_point_count (),
                                           NumberOfCells=self.get_cell_count ())

      element ['Points'] = VtkPointsElement (self.get_coordinates (), append=data, encoding=encoding)
      #element ['PointData'] = VtkPointDataElement (self._point_values, append=data, encoding=encoding)
      element ['PointData'] = VtkPointDataElement (self.get_point_fields (), append=data, encoding=encoding)
      element ['Cells'] = VtkCellsElement (self.get_connectivity (), self.get_offset (),
                                           self.get_types (), append=data, encoding=encoding)
      #element ['CellData'] = VtkCellDataElement (self._cell_values, append=data, encoding=encoding)
      element ['CellData'] = VtkCellDataElement (self.get_cell_fields (), append=data, encoding=encoding)

      if data is not None:
          element['AppendedData'] = data

      return element
  
  def root (self):
      return VtkRootElement ()
  def grid (self):
      return VtkGridElement ()
  def piece (self):
      return VtkPieceElement (NumberOfPoints=self.get_point_count (),
                              NumberOfCells=self.get_cell_count ())
  def points (self):
      return VtkPointsElement (self.get_coordinates (), append=data)
  def point_data (self):
      #return VtkPointDataElement (self._point_values, append=data)
      return VtkPointDataElement (self.get_point_fields (), append=data)
  def cells (self):
      VtkCellsElement (self.get_connectivity (), self.get_offset (),
                       self.get_types (), append=data)
  def cell_data (self):
      #return VtkCellDataElement (self._cell_values, append=data)
      return VtkCellDataElement (self.get_cell_fields (), append=data)

  def get_types (self):
      try:
          return self._types
      except AttributeError:
          types = []
          for offset in self.get_offset ():
              try:
                  n = offset - last_offset
              except NameError:
                  n = offset
              last_offset = offset
              if n==1:
                  type = 1
              elif n == 2:
                  type = 3
              elif n == 3:
                  type = 5
              elif n == 4:
                  type = 9
              else:
                  type = 7
              types.append (type)
          return np.array (types, dtype=np.uint8)
  def get_coordinates (self):
      return (self.get_x (), self.get_y (), self.get_z ())

def get_vtk_types (grid):
    offsets = grid.get_offset ()
    edge_count = np.diff (offsets)

    types = [int (edge_count_to_type.get (offsets[0], VtkPolygon))]
    for count in edge_count:
        types.append (int (edge_count_to_type.get (count, VtkPolygon)))
    return np.array (types, dtype=np.uint8)

def get_vtu_elements (field, format='ascii', encoding='ascii'):
    if format == 'appended':
        data = VtkAppendedDataElement ('', encoding=encoding)
    else:
        data = None

    element = {}
    element ['VTKFile'] = VtkRootElement ('UnstructuredGrid')
    element ['Grid'] = VtkGridElement ('UnstructuredGrid')
    element ['Piece'] = VtkPieceElement (NumberOfPoints=field.get_point_count (),
                                           NumberOfCells=field.get_cell_count ())

    coords = (field.get_x (), field.get_y (), field.get_z ())
    types = get_vtk_types (field)

    element ['Points'] = VtkPointsElement (coords, append=data, encoding=encoding)
    element ['PointData'] = VtkPointDataElement (field.get_point_fields (), append=data, encoding=encoding)
    element ['Cells'] = VtkCellsElement (field.get_connectivity (), field.get_offset (),
                                         types, append=data, encoding=encoding)
    element ['CellData'] = VtkCellDataElement (field.get_cell_fields (), append=data, encoding=encoding)

    if data is not None:
        element['AppendedData'] = data

    return element

from cmt.vtk import InvalidFormatError, InvalidEncodingError
from cmt.vtk import assemble_vtk_elements
from cmt.vtk import valid_formats, valid_encodings

def tofile (field, path, format='ascii', encoding='ascii'):
    """Write a field-like object to a VTK file.

    :param file: A field-like object
    :param path: Path to the file to write
    :keyword format: Specify the manner in which data is stored
    :type format: string ('ascii', 'binary', or 'appended')
    :keyword encoding: Specify the manner in which data is encoded
    :type encoding: string ('base64', or 'raw')

    Required methods of *field*,
        * get_point_count
        * get_cell_count
        * get_connectivity
        * get_offset
        * get_cell_fields
        * get_point_fields
        
    """
    if format not in valid_formats:
        raise InvalidFormatError (format)
    if encoding not in valid_encodings:
        raise InvalidEncodingError (encoding)

    if format == 'ascii':
        encoding = 'ascii'

    doc = xml.dom.minidom.Document ()

    elements = get_vtu_elements (field, format=format, encoding=encoding)
    doc.appendChild (assemble_vtk_elements (elements))

    with open (path, 'w') as f:
        f.write (doc.toprettyxml ())

class IDatabase (object):
    def __init__ (self):
        pass
    def open (self, path, var_name):
        pass
    def write (self, field):
        pass
    def close (self):
        pass

class Database (IDatabase):
    def open (self, path, var_name):
        try:
            self.close ()

            (root, ext) = os.path.splitext (path)

            self._var_name = var_name
            self._path = path
            self._template = '%s_%%04d%s' % (root, ext)
        except Exception as e:
            print 'Unable to open database: %s' % e

    def write (self, field, **kwargs):
        file_name = self._next_file_name ()
        tofile (field, file_name, **kwargs)

    def _next_file_name (self):
        try:
            next_file_name = self._template % self._count
        except AttributeError:
            self._count = 0
            next_file_name = self._template % self._count
        finally:
            self._count += 1

        return next_file_name

    def close (self):
        try:
            del self._count
        except AttributeError:
            pass


class VtkDatabase (object):
    def __init__ (self, field):
        self._field = field
        self._count = 0

    def tofile (self, path, **kwargs):
        (base, file) = os.path.split (path)
        (root, ext) = os.path.splitext (file)

        next_file = '%s_%04d%s' % (root, self._count, ext)

        tofile (self._field, os.path.join (base, next_file), **kwargs)

        self._count += 1

from xml.etree.ElementTree import ElementTree as ET

def fromfile (file):

    tree = ET ()
    tree.parse (file)
    root = tree.getroot ()

    if root.tag != 'VTKFile':
        raise MissingElementError ('Root element must be \'VTKFile\'')

    type = root.get ('type')
    version = root.get ('version')
    byte_order = root.get ('byte_order')
    if type is None or version is None or byte_order is None:
        raise MissingAttributeError ()

    data = root.find ('AppendedData')
    if data is not None:
        appended_data = data.text
        #appended_data = decode (data.text, encoding=data.get ('encoding', 'base64'))

    grid = root.find (type)
    piece = grid.find ('Piece')

    # For UnstructuredGrid
    cell_count = piece.get ('NumberOfCells')
    point_count = piece.get ('NumberOfPoints')

if __name__ == "__main__":
    import doctest
    doctest.testmod()

