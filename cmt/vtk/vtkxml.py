#! /bin/env python

import sys

import numpy as np
import xml.dom.minidom
#from cmt.encoders import ASCIIEncoder, RawEncoder, Base64Encoder
from cmt.vtk import encode
from vtktypes import sys_to_vtk_endian, np_to_vtk_type

class VtkElement (object, xml.dom.minidom.Element):
    def __init__ (self, name, **kwargs):
        xml.dom.minidom.Element.__init__ (self, str (name), namespaceURI='VTK')
        self.setAttributes (**kwargs)
    def setAttributes (self, **kwargs):
        for (attr, value) in kwargs.items ():
            self.setAttribute (attr, str (value))

class VtkTextElement (xml.dom.minidom.Text):
    def __init__ (self, text):
        self.replaceWholeText (text)

class VtkDataArrayElement (VtkElement):
    def __init__ (self, array, **kwargs):
        VtkElement.__init__ (self, 'DataArray', **kwargs)
    def addData (self, data_string):
        self.appendChild (VtkTextElement (data_string))

class VtkDataElement (VtkElement):
    format = 'ascii'
    def __init__ (self, name, **kwargs):
        VtkElement.__init__ (self, name)
    def addData (self, data, name, append=None, encoding='ascii', **kwargs):
        data_string = encode (data, encoding=encoding)
        #data_string = self.encode (data)
        data_array = VtkDataArrayElement (data_string, Name=name, 
                                          type=np_to_vtk_type[str (data.dtype)],
                                          **kwargs)
        self.appendChild (data_array)

        if append is not None:
            data_array.setAttributes (offset=append.offset (), format='appended')
            append.addData (data_string)
        else:
            data_array.setAttributes (format=self.format)
            data_array.addData (data_string)

class VtkRootElement (VtkElement):
    def __init__ (self, type):
        VtkElement.__init__ (self, 'VTKFile', type=type,
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
        xyz = np.vstack (coords).transpose ().flatten ()
        VtkDataElement.__init__ (self, 'Points', **kwargs)
        self.addData (xyz, 'Coordinates', NumberOfComponents=len (coords), **kwargs)

class VtkCoordinatesElement (VtkDataElement):
    def __init__ (self, xyz, **kwargs):
        VtkDataElement.__init__ (self, 'Coordinates', **kwargs)
        self.addData (xyz[0], 'x_coordinatess', NumberOfComponents=1, **kwargs)
        self.addData (xyz[1], 'y_coordinatess', NumberOfComponents=1, **kwargs)
        self.addData (xyz[2], 'z_coordinatess', NumberOfComponents=1, **kwargs)

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

