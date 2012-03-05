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

"""
import numpy as np

from cmt.grid import VTKGrid
from vtk import VtkWriter

from vtktypes import VtkUnstructured
from vtkxml import *

class VtkUnstructuredWriter (VTKGrid, VtkWriter):
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
      element ['Piece'] = VtkPieceElement (NumberOfPoints=self.point_count (),
                                           NumberOfCells=self.cell_count ())

      element ['Points'] = VtkPointsElement (self.get_coordinates (), append=data, encoding=encoding)
      element ['PointData'] = VtkPointDataElement (self._point_values, append=data, encoding=encoding)
      element ['Cells'] = VtkCellsElement (self.get_connectivity (), self.get_offset (),
                                           self.get_types (), append=data, encoding=encoding)
      element ['CellData'] = VtkCellDataElement (self._cell_values, append=data, encoding=encoding)

      if data is not None:
          element['AppendedData'] = data

      return element
  
  def root (self):
      return VtkRootElement ()
  def grid (self):
      return VtkGridElement ()
  def piece (self):
      return VtkPieceElement (NumberOfPoints=self.point_count (),
                              NumberOfCells=self.cell_count ())
  def points (self):
      return VtkPointsElement (self.get_coordinates (), append=data)
  def point_data (self):
      return VtkPointDataElement (self._point_values, append=data)
  def cells (self):
      VtkCellsElement (self.get_connectivity (), self.get_offset (),
                       self.get_types (), append=data)
  def cell_data (self):
      return VtkCellDataElement (self._cell_values, append=data)

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

if __name__ == "__main__":
    import doctest
    doctest.testmod()

