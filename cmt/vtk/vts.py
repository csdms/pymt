#! /bin/env python
"""
Examples
========

A structured grid
-----------------

    >>> (x, y) = np.meshgrid ([-1., 1., 3., 5.], [-.5, .5, 1.5])
    >>> g = VtkStructuredWriter (x, y, (3, 4))
    >>> g.add_point_data ('Elevation', np.arange (12.))
    >>> g.add_cell_data ('Cell Elevation', [1., 2., 3, 4, 5, 6])
    >>> g.write ('rect.vts', format='appended', encoding='base64')

"""
from cmt.grid import VTKGridStructured
from vtk import VtkWriter

from vtktypes import VtkStructured
from vtkxml import *

class VtkStructuredWriter (VTKGridStructured, VtkWriter):
  _vtk_grid_type = VtkStructured

  def __init__ (self, *args, **kwargs):
    super (VtkStructuredWriter, self).__init__ (*args)
    VtkWriter.__init__ (self)

  def get_elements (self, format='ascii', encoding='ascii'):
      if format == 'appended':
          data = VtkAppendedDataElement ('', encoding=encoding)
      else:
          data = None

      shape = self.get_shape ()

      element = {}
      element ['VTKFile'] = VtkRootElement (VtkStructured)
      element ['Grid'] = VtkGridElement (VtkStructured,
                                         WholeExtent='0 %d 0 %d 0 0' % (shape[1], shape[0]))
      element ['Piece'] = VtkPieceElement (Extent='0 %d 0 %d 0 0' % (shape[1], shape[0]))

      element ['Points'] = VtkPointsElement (self.get_coordinates (), append=data, encoding=encoding)
      element ['PointData'] = VtkPointDataElement (self._point_values, append=data, encoding=encoding)
      element ['CellData'] = VtkCellDataElement (self._cell_values, append=data, encoding=encoding)

      if data is not None:
          element['AppendedData'] = data

      return element
  
if __name__ == "__main__":
    import doctest
    doctest.testmod()

