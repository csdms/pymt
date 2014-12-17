#! /bin/env python
"""
Examples
========

Define a grid that consists of two trianges that share two points.

::

       (2) - (3)
      /   \  /
    (0) - (1)

Create the grid,

>>> from cmt.printers.vtk import tofile

>>> from cmt.grids.field import GridField
>>> g = GridField ([0, 2, 1, 3], [0, 0, 1, 1], [0, 2, 1, 2, 3, 1], [3, 6])
>>> g.add_field ('Elevation',  [1., 2., 3, 4], centering='point')
>>> g.add_field ('Temperature',  [10., 20., 30., 40.], centering='point')
>>> g.add_field ('Cell Elevation', [1., 2.], centering='zonal')
>>> g.add_field ('Cell Temperature', [10., 20.], centering='zonal')
>>> tofile (g, 'tri.vtu', format='appended', encoding='base64')
"""
import os
import xml.dom.minidom


valid_encodings = ['ascii', 'base64', 'raw']
valid_formats = ['ascii', 'base64', 'raw', 'appended']


class VtkError(Exception):
    pass


class InvalidFormatError(VtkError):
    def __init__(self, fmt):
        self.name = fmt

    def __str__(self):
        return '%s: Invalid format' % self.name


class InvalidEncodingError(VtkError):
    def __init__(self, encoding):
        self.name = encoding
    def __str__(self):
        return '%s: Invalid encoder' % self.name


class VtkWriter(xml.dom.minidom.Document):
    def __init__(self):
        xml.dom.minidom.Document.__init__(self)

    def get_elements(self, **kwds):
        raise NotImplementedError('get_elements')

    def assemble(self, element):
        root = element['VTKFile']
        grid = element['Grid']
        piece = element['Piece']
        for section in ['Points', 'Coordinates', 'PointData', 'Cells',
                        'CellData']:
            try:
                piece.appendChild(element[section])
            except KeyError:
                pass
        grid.appendChild(piece)
        root.appendChild(grid)
  
        try:
            root.appendChild(element['AppendedData'])
        except KeyError:
            pass
  
        return root
  
    def write(self, path, fmt='ascii', encoding='ascii'):
        if fmt not in valid_formats:
            raise InvalidFormatError(fmt)
        if encoding not in valid_encodings:
            raise InvalidEncodingError(encoding)
  
        if fmt == 'ascii':
            encoding = 'ascii'
  
        self.unlink()
        self.appendChild(self.assemble(self.get_elements(format=fmt,
                                                         encoding=encoding)))
        self.to_xml(path)
  
    def to_xml(self, path):
        file = open(path, 'w')
        file.write(self.toprettyxml())
        file.close()


def assemble_vtk_elements(element):
    root = element['VTKFile']
    grid = element['Grid']
    piece = element['Piece']
    for section in ['Points', 'Coordinates', 'PointData', 'Cells', 'CellData']:
        try:
            piece.appendChild(element[section])
        except KeyError:
            pass
    grid.appendChild(piece)
    root.appendChild(grid)

    try:
        root.appendChild(element['AppendedData'])
    except KeyError:
        pass

    return root


class VtkDatabase(VtkWriter):
    def write(self, path, **kwargs):
        (base, file) = os.path.split(path)
        (root, ext) = os.path.splitext(file)

        try:
            next_file = '%s_%04d%s' % (root, self._count, ext)
        except NameError:
            self._count = 0
            next_file = '%s_%04d%s' % (root, self._count, ext)

        VtkWriter.write(self, os.path.join (base, next_file), **kwargs)

        self._count += 1
