#! /bin/env python
"""
Examples
========

A structured grid
-----------------

    >>> (x, y) = np.meshgrid ([-1., 1., 3., 5.], [-.5, .5, 1.5])
    >>> g = VtkStructuredWriter (x, y, (3, 4))
    >>> g.get_point_count ()
    12
    >>> g.get_cell_count ()
    6
    >>> g.add_field ('Elevation', np.arange (12.), centering='point')
    >>> g.add_field ('Cell Elevation', [1., 2., 3, 4, 5, 6], centering='zonal')

    >>> format, encoding =('appended', 'base64')
    
    >>> g.write ('rect.vts', format=format, encoding=encoding)

    #>>> g.write ('rect.vts')

"""
from cmt.grids import StructuredField
#from cmt.grid import VTKGridStructured
from vtk import VtkWriter

from vtktypes import VtkStructured
from vtkxml import *

class VtkStructuredWriter (StructuredField, VtkWriter):
#class VtkStructuredWriter (VTKGridStructured, VtkWriter):
  _vtk_grid_type = VtkStructured

  def __init__ (self, *args, **kwargs):
    super (VtkStructuredWriter, self).__init__ (*args)
    VtkWriter.__init__ (self)

  def get_elements (self, format='ascii', encoding='ascii'):
      if format == 'appended':
          data = VtkAppendedDataElement ('', encoding=encoding)
      else:
          data = None

      extent = VtkExtent (self.get_shape ()[::-1])

      element = {}
      element ['VTKFile'] = VtkRootElement (VtkStructured)
      element ['Grid'] = VtkGridElement (VtkStructured,
                                         WholeExtent=extent)
                                         #WholeExtent='0 %d 0 %d 0 0' % (shape[1]-1, shape[0]-1))
      element ['Piece'] = VtkPieceElement (Extent=extent)
      #element ['Piece'] = VtkPieceElement (Extent='0 %d 0 %d 0 0' % (shape[1]-1, shape[0]-1))

      element ['Points'] = VtkPointsElement (self.get_xyz (), append=data, encoding=encoding)
      element ['PointData'] = VtkPointDataElement (self.get_point_fields (), append=data, encoding=encoding)
      #element ['PointData'] = VtkPointDataElement (self._point_values, append=data, encoding=encoding)
      element ['CellData'] = VtkCellDataElement (self.get_cell_fields (), append=data, encoding=encoding)
      #element ['CellData'] = VtkCellDataElement (self._cell_values, append=data, encoding=encoding)

      if data is not None:
          element['AppendedData'] = data

      return element

  #def get_extent (self):
  #    shape = self.get_shape ()
  #    extent = []
  #    for n in shape[::-1]:
  #        extent.append ('0 %d' % (n-1))
  #    return ' '.join (extent) + ' 0 0'*(3-len (shape))
      
  
if __name__ == "__main__":
    import doctest
    doctest.testmod()

