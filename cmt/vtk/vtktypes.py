#! /bin/env python

from cmt.encoders import ASCIIEncoder, RawEncoder, Base64Encoder

class VtkEndian (object):
    def __init__ (self, endian):
        self.name = endian
    def __str__ (self):
        return self.name
VtkLittleEndian = VtkEndian ('LittleEndian')
VtkBigEndian = VtkEndian ('BigEndian')

sys_to_vtk_endian = {'little': VtkLittleEndian,
                     'big': VtkBigEndian}

class VtkType (object):
    def __init__ (self, name, size):
        self.bytes = size
        self.name = name
    def __str__ (self):
        return self.name

VtkUInt8 = VtkType ('UInt8', 1)
VtkInt32 = VtkType ('Int32', 4)
VtkInt64 = VtkType ('Int64', 8)
VtkFloat32 = VtkType ('Float32', 4)
VtkFloat64 = VtkType ('Float64', 8)

np_to_vtk_type = {'uint8': VtkUInt8,
                  'int32': VtkInt32, 'int64': VtkInt64,
                  'float32': VtkFloat32, 'float64': VtkFloat64}

class VtkCellType (object):
    def __init__ (self, name, id):
        self.id = id
        self.name = name
    def __str__ (self):
        return self.name
VtkVertex = VtkCellType ('Vertex', 1)
VtkLine = VtkCellType ('Line', 3)
VtkTriangle = VtkCellType ('Triangle', 5)
VtkPolygon = VtkCellType ('Polygon', 7)

class VtkGridType (object):
    def __init__ (self, name):
        self.name = name
    def __str__ (self):
        return self.name

VtkUniformRectilinear = VtkGridType ('ImageData')
VtkRectilinear = VtkGridType ('RectilinearGrid')
VtkStructured = VtkGridType ('StructuredGrid')
VtkUnstructured = VtkGridType ('UnstructuredGrid')

encoders = {'ascii': ASCIIEncoder (), 'raw': RawEncoder (),
            'base64': Base64Encoder ()}

