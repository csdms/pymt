#! /bin/env python
import sys

import numpy as np
from six.moves import xrange
import xml.dom.minidom

from .encoders import encode
from .vtktypes import sys_to_vtk_endian, np_to_vtk_type

class VtkExtent (object):
    def __init__ (self, shape):
        assert (len (shape)<=3)

        self._shape = shape

        self._extent = []
        for n in shape:
            self._extent.append ((0, n-1))
        for n in xrange (3-len (shape)):
            self._extent.append ((0, 0))

        self._extent_str = ' '.join (['%d %d' % x for x in self._extent])
        
    def __str__ (self):
        return self._extent_str
        
class VtkOrigin (object):
    def __init__ (self, origin, spacing):
        assert (len (spacing)<=3)
        assert (len (spacing)==len (origin))

        self._spacing = spacing
        self._cell_origin = origin

        self._cell_origin = []
        for (dx, x0) in zip (spacing, origin):
            self._cell_origin.append (x0 - dx*.5)

        for _ in xrange (3-len (origin)):
            self._cell_origin.append (0.)

        self._origin_str = ' '.join (['%f' % x for x in self._cell_origin])
        
    def __str__ (self):
        return self._origin_str
    
class VtkSpacing (object):
    def __init__ (self, spacing):
        assert (len (spacing)<=3)

        self._spacing = spacing

        self._padded_spacing = []
        for dx in spacing:
            self._padded_spacing.append (dx)
        for _ in xrange (3-len (spacing)):
            self._padded_spacing.append (0.)

        self._spacing_str = ' '.join (['%f' % x for x in self._padded_spacing])
        
    def __str__ (self):
        return self._spacing_str
    
class VtkElement (object, xml.dom.minidom.Element):
    def __init__ (self, name, **kwargs):
        xml.dom.minidom.Element.__init__ (self, str (name), namespaceURI='VTK')
        self.setAttributes (**kwargs)

    def setAttributes (self, **kwargs):
        for (attr, value) in kwargs.items ():
            self.setAttribute (attr, str (value))

    def getAttributes (self, names=None):
        attrs = {}

        if names is None:
            for i in range (self.attributes.length):
                attr = self.attributes.item (i)
                attrs[attr.localName] = attr.value
        else:
            for i in range (self.attributes.length):
                attr = self.attributes.item (i)
                if attr.localName in names:
                    attrs[attr.localName] = attr.value

        return attrs


class VtkTextElement (xml.dom.minidom.Text):
    def __init__ (self, text):
        self.replaceWholeText (text)


class VtkDataArrayElement (VtkElement):
    def __init__(self, **kwargs):
        VtkElement.__init__(self, 'DataArray', **kwargs)

    def addData(self, data_string):
        self.appendChild(VtkTextElement(data_string))

class VtkDataElement (VtkElement):
    format = 'ascii'
    def __init__(self, name, **kwargs):
        VtkElement.__init__ (self, name)

    def addData (self, data, name, append=None, encoding='ascii', **kwargs):
        data_string = encode(data, encoding=encoding)
        data_array = VtkDataArrayElement(Name=name,
                                         type=np_to_vtk_type[str(data.dtype)],
                                         **kwargs)
        self.appendChild(data_array)

        if append is not None:
            data_array.setAttributes(offset=append.offset (), format='appended')
            append.addData(data_string)
        else:
            data_array.setAttributes(format=self.format)
            data_array.addData(data_string)


class VtkRootElement (VtkElement):
    def __init__ (self, root_type):
        VtkElement.__init__ (self, 'VTKFile', type=root_type,
                             version='0.1',
                             byte_order=str (sys_to_vtk_endian[sys.byteorder]))

class VtkGridElement (VtkElement):
    def __init__ (self, name, **kwargs):
        VtkElement.__init__ (self, name, **kwargs)

class VtkPieceElement (VtkElement):
    def __init__ (self, **kwargs):
        VtkElement.__init__ (self, "Piece", **kwargs)

class VtkAppendedDataElement (VtkElement):
    def __init__ (self, data, **kwargs):
        VtkElement.__init__ (self, 'AppendedData', **kwargs)
        self.appendChild (VtkTextElement ('_'+data))
    def addData (self, data):
        self.firstChild.appendData (data)
    def offset (self):
        return self.firstChild.length-1

class VtkPointsElement (VtkDataElement):
    def __init__ (self, coords, **kwargs):
        n_components = 3
        xyz = []
        for i in xrange (n_components):
            try:
                xyz.append (coords[i])
            except IndexError:
                xyz.append (np.array (coords[0])*0)
        xyz = np.vstack (xyz).transpose ().flatten ()
        VtkDataElement.__init__ (self, 'Points', **kwargs)
        self.addData (xyz, 'Coordinates', NumberOfComponents=n_components, **kwargs)

class VtkCoordinatesElement (VtkDataElement):
    def __init__ (self, xyz, **kwargs):
        VtkDataElement.__init__ (self, 'Coordinates', **kwargs)
        for (i, label) in enumerate (['x', 'y', 'z']):
            try:
                self.addData (xyz[i], label +'_coordinates', NumberOfComponents=1, **kwargs)
            except IndexError:
                self.addData (np.array (xyz[0])*0., label +'_coordinates', NumberOfComponents=1, **kwargs)

        #self.addData (xyz[0], 'x_coordinates', NumberOfComponents=1, **kwargs)
        #self.addData (xyz[1], 'y_coordinates', NumberOfComponents=1, **kwargs)
        #self.addData (xyz[2], 'z_coordinates', NumberOfComponents=1, **kwargs)

class VtkCellsElement (VtkDataElement):
    def __init__ (self, connectivity, offset, types, **kwargs):
        VtkDataElement.__init__ (self, 'Cells', **kwargs)
        self.addData (connectivity, 'connectivity', **kwargs)
        self.addData (offset, 'offsets', **kwargs)
        self.addData (types, 'types', **kwargs)

class VtkPointDataElement (VtkDataElement):
    def __init__ (self, values, **kwargs):
        VtkDataElement.__init__ (self, 'PointData', **kwargs)
        for (name, value) in values.items ():
            self.addData (value, name, NumberOfComponents=1, **kwargs)

class VtkCellDataElement (VtkDataElement):
    def __init__ (self, values, **kwargs):
        VtkDataElement.__init__ (self, 'CellData', **kwargs)
        for (name, value) in values.items ():
            self.addData (value, name, NumberOfComponents=1, **kwargs)

