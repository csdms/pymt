#! /bin/env python
from .vtktypes import VtkRectilinear
from .vtkxml import (VtkAppendedDataElement, VtkExtent, VtkRootElement,
                     VtkGridElement, VtkPieceElement, VtkCoordinatesElement,
                     VtkPointDataElement, VtkCellDataElement)


def get_elements(field, data_format='ascii', encoding='ascii'):
    if data_format == 'appended':
        data = VtkAppendedDataElement('', encoding=encoding)
    else:
        data = None

    extent = VtkExtent(field.get_shape()[::-1])

    element = {
        'VTKFile': VtkRootElement(VtkRectilinear),
        'Grid': VtkGridElement(VtkRectilinear, WholeExtent=extent),
        'Piece': VtkPieceElement(Extent=extent),
        'Coordinates': VtkCoordinatesElement(field.get_xyz_coordinates(),
                                             append=data, encoding=encoding),
        'PointData': VtkPointDataElement(field.get_point_fields(),
                                         append=data, encoding=encoding),
        'CellData': VtkCellDataElement(field.get_cell_fields(), append=data,
                                       encoding=encoding),
    }

    if data is not None:
        element['AppendedData'] = data

    return element
