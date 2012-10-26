#! /bin/env python
"""
Examples
========

A rectilinear grid
------------------

    >>> g = VtkRectilinearWriter ([-1., 1., 3., 5.], [-.5, .5, 1.5], encoding='base64')
    >>> g.add_field ('Elevation', np.arange (12.), centering='point')
    >>> g.add_field ('Cell Elevation', [1., 2., 3, 4, 5, 6], centering='zonal')
    >>> g.write ('rect.vtr')

"""
#from cmt.grid import VTKGridRectilinear
from cmt.grids import RectilinearField
from vtk import VtkWriter

from vtktypes import VtkRectilinear
from vtkxml import *

class VtkRectilinearWriter (RectilinearField, VtkWriter):
#class VtkRectilinearWriter (VTKGridRectilinear, VtkWriter):
  _vtk_grid_type = VtkRectilinear

  def __init__ (self, *args, **kwargs):
    super (VtkRectilinearWriter, self).__init__ (*args)
    VtkWriter.__init__ (self)

  def get_elements (self, format='ascii', encoding='ascii'):
      if format == 'appended':
          data = VtkAppendedDataElement ('', encoding=encoding)
      else:
          data = None

      #shape = self.get_shape ()
      extent = VtkExtent (self.get_shape ()[::-1])

      element = {}
      element ['VTKFile'] = VtkRootElement (VtkRectilinear)
      element ['Grid'] = VtkGridElement (VtkRectilinear, WholeExtent=extent)
                                         #WholeExtent='0 %d 0 %d 0 0' % (shape[1], shape[0]))
      element ['Piece'] = VtkPieceElement (Extent=extent)
      #Extent='0 %d 0 %d 0 0' % (shape[1], shape[0]))

      element ['Coordinates'] = VtkCoordinatesElement (self.get_xyz_coordinates (), append=data, encoding=encoding)
      element ['PointData'] = VtkPointDataElement (self.get_point_fields (), append=data, encoding=encoding)
      element ['CellData'] = VtkCellDataElement (self.get_cell_fields (), append=data, encoding=encoding)

      if data is not None:
          element['AppendedData'] = data

      return element
  
if __name__ == "__main__":
    import doctest
    doctest.testmod()

