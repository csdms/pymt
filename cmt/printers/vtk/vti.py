#! /bin/env python
from .vtktypes import VtkUniformRectilinear
from .vtkxml import *


def extent_string(shape):
    return '0 %d 0 %d 0 0' % (shape[1], shape[0])


def origin_string(origin, spacing):
    return '%f %f 0.' % (origin[1] - spacing[1] * .5,
                         origin[0] - spacing[0] * .5)


def spacing_string(spacing):
    return '%f %f 0.' % (spacing[1], spacing[0])


def get_elements(field, data_format='ascii', encoding='ascii'):
    if data_format == 'appended':
        data = VtkAppendedDataElement('', encoding=encoding)
    else:
        data = None

    extent = VtkExtent(field.get_shape()[::-1])
    origin = VtkOrigin(field.get_origin()[::-1], field.get_spacing()[::-1])
    spacing = VtkSpacing(field.get_spacing()[::-1])

    element = {
        'VTKFile': VtkRootElement(VtkUniformRectilinear),
        'Grid': VtkGridElement(VtkUniformRectilinear, WholeExtent=extent,
                               Origin=origin, Spacing=spacing),
        'Piece': VtkPieceElement(Extent=extent),
        'PointData': VtkPointDataElement(field.get_point_fields(),
                                         append=data, encoding=encoding),
        'CellData': VtkCellDataElement(field.get_cell_fields(), append=data,
                                       encoding=encoding),
    }

    if data is not None:
        element['AppendedData'] = data

    return element
