#! /bin/env python

import os
from collections import namedtuple
from xml.etree.ElementTree import ElementTree

from ...grids import UnstructuredField

from .vtktypes import edge_count_to_type, VtkPolygon, vtk_to_np_type
from .vtkxml import *
from .vtk import InvalidFormatError, InvalidEncodingError
from .vtk import assemble_vtk_elements
from .vtk import valid_formats, valid_encodings


class Error(Exception):
    pass


class MissingAttributeError(Error):
    pass


class MissingElementError(Error):
    pass


def get_vtk_types(grid):
    offsets = grid.get_offset()
    edge_count = np.diff(offsets)

    types = [int(edge_count_to_type.get(offsets[0], VtkPolygon))]
    for count in edge_count:
        types.append(int(edge_count_to_type.get(count, VtkPolygon)))
    return np.array(types, dtype=np.uint8)


def get_vtu_elements(field, data_format='ascii', encoding='ascii'):
    if data_format == 'appended':
        data = VtkAppendedDataElement('', encoding=encoding)
    else:
        data = None

    coords = field.get_coordinate(range(field.get_dim_count()))
    types = get_vtk_types(field)

    element = {
        "VTKFile": VtkRootElement('UnstructuredGrid'),
        "Grid": VtkGridElement('UnstructuredGrid'),
        "Piece": VtkPieceElement(NumberOfPoints=field.get_point_count(),
                                 NumberOfCells=field.get_cell_count()),
        "Points": VtkPointsElement(coords, append=data, encoding=encoding),
        "PointData": VtkPointDataElement(field.get_point_fields(),
                                         append=data, encoding=encoding),
        "Cells": VtkCellsElement(field.get_connectivity(),
                                 field.get_offset(), types, append=data,
                                 encoding=encoding),
        "CellData": VtkCellDataElement(field.get_cell_fields(),
                                       append=data, encoding=encoding),
    }

    if data is not None:
        element['AppendedData'] = data

    return element


def tofile(field, path, **kwds):
    """Write a field-like object to a VTK file.

    Parameters
    ----------
    field : field-like
        Field to write to vtk.
    path : str
        Path to the file to write.
    format : {'ascii', 'binary', 'appended'}
        Format in which data is stored in the vtk file.
    encoding : {'base64', 'raw'}
        Encoding method for data in vtk file.

    Notes
    -----
    The *field* object must implement all of the following methods:
        * get_point_count
        * get_cell_count
        * get_connectivity
        * get_offset
        * get_cell_fields
        * get_point_fields
    """
    data_format = kwds.get('format', 'ascii')
    encoding = kwds.get('encoding', 'ascii')

    if data_format not in valid_formats:
        raise InvalidFormatError(data_format)
    if encoding not in valid_encodings:
        raise InvalidEncodingError(encoding)

    if data_format == 'ascii':
        encoding = 'ascii'

    doc = xml.dom.minidom.Document()

    elements = get_vtu_elements(field, data_format=data_format,
                                encoding=encoding)
    doc.appendChild(assemble_vtk_elements(elements))

    with open(path, 'w') as f:
        f.write(doc.toprettyxml())


class IDatabase(object):
    def __init__(self):
        pass

    def open(self, path, var_name):
        pass

    def write(self, field):
        pass

    def close(self):
        pass


class Database(IDatabase):
    def __init__(self):
        self._var_name = ""
        self._path = ""
        self._template = ""

        super(Database, self).__init__()

    def open(self, path, var_name):
        try:
            self.close()

            (root, ext) = os.path.splitext(path)

            self._var_name = var_name
            self._path = path
            self._template = '%s_%%04d%s' % (root, ext)
        except Exception as e:
            print 'Unable to open database: %s' % e

    def write(self, field, **kwargs):
        file_name = self._next_file_name()
        tofile(field, file_name, **kwargs)

    def _next_file_name(self):
        try:
            next_file_name = self._template % self._count
        except AttributeError:
            self._count = 0
            next_file_name = self._template % self._count
        finally:
            self._count += 1

        return next_file_name

    def close(self):
        try:
            del self._count
        except AttributeError:
            pass


class VtkDatabase(object):
    def __init__(self, field):
        self._field = field
        self._count = 0

    def tofile(self, path, **kwargs):
        (base, filename) = os.path.split(path)
        (root, ext) = os.path.splitext(filename)

        next_file = '%s_%04d%s' % (root, self._count, ext)

        tofile(self._field, os.path.join(base, next_file), **kwargs)

        self._count += 1


DataArray = namedtuple('DataArray', ['name', 'data'])
Piece = namedtuple('Piece', ['points', 'cells', 'point_data', 'cell_data'])
Point = namedtuple('Point', ['x', 'y', 'z'])
Cell = namedtuple('Cell', ['connectivity', 'offsets', 'types'])


def parse_data_array(data_array):
    assert(data_array.tag == 'DataArray')

    name = data_array.get('Name')
    noc = data_array.get('NumberOfComponents', default='1')
    data_type = data_array.get('type')
    data_format = data_array.get('format', default='ascii')

    noc = int(noc)

    assert(data_format == 'ascii')

    data = [float(val) for val in data_array.text.split()]
    array = np.array(data, dtype=vtk_to_np_type[data_type])

    components = []
    for i in range(noc):
        components.append(array[i::noc])

    return DataArray(name, components)


def parse_all_data_array(element):
    d = {}
    for data_array in element.findall('DataArray'):
        data = parse_data_array(data_array)
        d[data.name] = data.data

    return d


def parse_points(points):
    assert(points.tag == 'Points')

    data = parse_data_array(points.find('DataArray'))

    n_points = len(data.data[0])
    components = data.data
    for i in range(3 - len(data.data)):
        components.append(np.zeros(n_points))

    return Point(components[0], components[1], components[2])


def parse_cells(cells):
    assert(cells.tag == 'Cells')

    d = parse_all_data_array(cells)
    for (key, value) in d.items():
        d[key] = value[0]

    return Cell(**d)


def parse_piece(piece):
    assert(piece.tag == 'Piece')

    cell_count = int(piece.get('NumberOfCells'))
    point_count = int(piece.get('NumberOfPoints'))

    points = parse_points(piece.find('Points'))
    cells = parse_cells(piece.find('Cells'))

    point_data = parse_all_data_array(piece.find('PointData'))
    cell_data = parse_all_data_array(piece.find('CellData'))

    assert(cell_count == len(cells.offsets))
    assert(cell_count == len(cells.types))
    assert(point_count == len(points.x))
    assert(point_count == len(points.y))
    assert(point_count == len(points.z))
    
    return Piece(points=points, cells=cells,
                 point_data=point_data, cell_data=cell_data)


def fromfile(source):
    """
    Parameters
    ----------
    source : str or file-like
        Name of file or file object containing XML data.

    Returns
    -------
    UnstructuredField
        The parsed data field.
    """
    tree = ElementTree()
    tree.parse(source)
    root = tree.getroot()

    if root.tag != 'VTKFile':
        raise MissingElementError('Root element must be \'VTKFile\'')

    data_type = root.get('type')
    version = root.get('version')
    byte_order = root.get('byte_order')
    if data_type is None or version is None or byte_order is None:
        raise MissingAttributeError()

    #data = root.find ('AppendedData')
    #if data is not None:
    #    appended_data = data.text
    #    #appended_data = decode(data.text, encoding=data.get('encoding',
    #    #                                                    'base64'))

    grid = root.find(data_type)
    piece = parse_piece(grid.find('Piece'))

    points = piece.points
    cells = piece.cells

    field = UnstructuredField(points.x, points.y, cells.connectivity,
                              cells.offsets)
    for (key, val) in piece.point_data.items():
        field.add_field(key, val, centering='point')
    for (key, val) in piece.cell_data.items():
        field.add_field(key, val, centering='zonal')

    return field
