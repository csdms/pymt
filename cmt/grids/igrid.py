

CENTERING_CHOICES = ['zonal', 'point']


class Error(Exception):
    """Base class for grid and field errors""" 
    pass


class DimensionError(Error):
    """Error to indicate a dimension mismatch when adding a value field to a grid."""
    def __init__(self, dim0, dim1):
        try:
            self.src_dim = tuple(dim0)
        except TypeError:
            self.src_dim = dim0

        try:
            self.dst_dim = tuple(dim1)
        except TypeError:
            self.dst_dim = dim1

    def __str__(self):
        return '%s != %s' % (self.src_dim, self.dst_dim)


class CenteringValueError(Error):
    """Error to indicate an invalid value for value centering."""
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return "%s: Bad value for 'centering'" % self.val


class GridTypeError(Error):
    def __str__(self):
        try:
            return 'Grid is not %s' % self.type
        except AttributeError:
            return 'Grid is not of required type'


class NonUniformGridError(GridTypeError):
    """Error to indicate a grid is not a uniform rectilinear grid"""
    type = 'uniform rectilinear'


class NonStructuredGridError(GridTypeError):
    """Error to indicate a grid is not a structured grid"""
    type = 'structured'


class IGrid(object):
    """An interface for a grid object that represents a structured or unstructured
       grid of nodes and elements.
    """
    def get_x(self):
        """Return the x-coordinates of the grid nodes."""
        pass
    def get_y(self):
        """Return the y-coordinates of the grid nodes."""
        pass
    def get_connectivity(self):
        """Return the connectivity array for the grid."""
        pass
    def get_offset(self):
        """Return an array of offsets in to the connectivity array for each
           element of the grid."""
        pass


class IField(IGrid):
    def get_field(self, field_name):
        """Return an array of values for the requested field"""
        pass
