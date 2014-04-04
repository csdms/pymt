#! /bin/env python
"""
Examples
========

A uniform rectilinear grid
--------------------------

Create a uniform rectilinear grid that looks like the following,

::

    (0) - (1) - (2) - (3)
     |     |     |     |
    (4) - (5) - (6) - (7)
     |     |     |     |
    (8) - (9) - (10)-(11)

>>> g = VtkUniformRectilinearWriter ([4, 3], [2, 1.], [0, 0], encoding='base64')
>>> g.get_point_count ()
12
>>> g.get_cell_count ()
6
>>> g.add_field ('Elevation', np.arange (12.), centering='point')
>>> g.add_field ('Cell Elevation', [1., 2., 3, 4, 5, 6], centering='zonal')
>>> g.write ('rect.vti')
"""
from cmt.grids import RasterField
from .vtk import VtkWriter

from .vtktypes import VtkUniformRectilinear
from .vtkxml import *

def extent_string (shape):
    return '0 %d 0 %d 0 0' % (shape[1], shape[0])
def origin_string (origin, spacing):
    return '%f %f 0.' % (origin[1]-spacing[1]*.5, origin[0]-spacing[0]*.5)
def spacing_string (spacing):
    return '%f %f 0.' % (spacing[1], spacing[0])

#class VtkUniformRectilinearWriter (VTKGridUniformRectilinear, VtkWriter):
class VtkUniformRectilinearWriter (RasterField, VtkWriter):
  _vtk_grid_type = VtkUniformRectilinear

  def __init__ (self, *args, **kwargs):
    super (VtkUniformRectilinearWriter, self).__init__ (*args)
    VtkWriter.__init__ (self)

  def get_elements (self, format='ascii', encoding='ascii'):
      if format == 'appended':
          data = VtkAppendedDataElement ('', encoding=encoding)
      else:
          data = None

      #shape = self.get_shape ()
      #origin = self.get_origin ()
      #spacing = self.get_spacing ()

      extent = VtkExtent (self.get_shape ()[::-1])
      origin = VtkOrigin (self.get_origin ()[::-1], self.get_spacing ()[::-1])
      spacing = VtkSpacing (self.get_spacing ()[::-1])

      element = {}
      element ['VTKFile'] = VtkRootElement (VtkUniformRectilinear)
      element ['Grid'] = VtkGridElement (VtkUniformRectilinear,
                                         WholeExtent=extent,
                                         Origin=origin,
                                         Spacing=spacing)
                                         #WholeExtent=extent_string (shape),
                                         #Origin=origin_string (origin, spacing),
                                         #Spacing=spacing_string (spacing))
      element ['Piece'] = VtkPieceElement (Extent=extent)

      element ['PointData'] = VtkPointDataElement (self.get_point_fields (), append=data, encoding=encoding)
      element ['CellData'] = VtkCellDataElement (self.get_cell_fields (), append=data, encoding=encoding)

      if data is not None:
          element['AppendedData'] = data

      return element
  
if __name__ == "__main__":
    import doctest
    doctest.testmod()

