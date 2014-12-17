import os
import string
import warnings

import numpy as np


from ..grids import RasterField, StructuredField, UnstructuredField

class Error(Exception):
    pass


class DimensionError(Error):
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class BadFileFormatError(Error):
    def __init__(self, fmt):
        self._format = fmt

    def __str__(self):
        return self._format



def positive_dimensions(shape):
    return shape[shape > 0]


def find_unknown_dimension(shape):
    (unknown_dim, ) = np.where(np.array(shape) < 0)
    if len(unknown_dim) > 1:
        raise DimensionError('more than one unknown dimension')
    try:
        return unknown_dim[0]
    except IndexError:
        return None


def fix_unknown_shape(shape, size):
    """
    >>> print fix_unknown_shape((4, 3), 12)
    (4, 3)
    >>> print fix_unknown_shape((4, -1), 12)
    (4, 3)
    """
    if len(shape) > 0:
        new_shape = np.array(shape)
    else:
        if size != 0:
            raise DimensionError('total size of new array must be unchanged')
        return (0, )

    known_element_count = np.prod(new_shape[new_shape > 0])
    if size % known_element_count != 0:
        raise DimensionError('total size of new array must be unchanged')

    unknown_dim = find_unknown_dimension(new_shape)
    if unknown_dim is not None:
        new_shape[unknown_dim] = size / known_element_count

    return tuple(new_shape)


def is_structured_port(port, var_name):
    if hasattr(port, 'get_grid_shape'):
        shape = port.get_grid_shape(var_name)
        if shape is None:
            return False
    else:
        return False
    return True


def is_rectilinear_port(port, var_name):
    if is_structured_port(port, var_name) and hasattr(port, 'get_grid_spacing'):
        spacing = port.get_grid_spacing(var_name)
        if spacing is None:
            return False
    else:
        return False
    return True


def port_is_one_point(port, var_name):
    shape = port.get_grid_shape(var_name)
    if len(shape) == 1 and shape[0] == 1:
        return True
    else:
        return False


def _port_shape_as_array(port, var_name):
    return port.get_grid_shape(var_name)


def _port_spacing_as_array(port, var_name):
    if port_is_one_point(port, var_name):
        spacing = np.array([1.])
    else:
        spacing = port.get_grid_spacing(var_name)
    return spacing


def _port_origin_as_array(port, var_name):
    if port_is_one_point(port, var_name):
        origin = np.array([0.])
    else:
        try:
            origin = port.get_grid_origin(var_name)
        except AttributeError:
            origin = port.get_grid_lower_left(var_name)
            warnings.warn('get_grid_lower_left', DeprecationWarning)
    return origin


def _construct_port_as_rectilinear_field(port, var_name, data_array):
    shape = _port_shape_as_array(port, var_name)
    spacing = _port_spacing_as_array(port, var_name)
    origin = _port_origin_as_array(port, var_name)

    shape = fix_unknown_shape(shape, data_array.size)

    return RasterField(shape, spacing, origin, indexing='ij')


def _construct_port_as_structured_field(port, var_name, data_array):
    shape = _port_shape_as_array(port, var_name)
    shape = fix_unknown_shape(shape, data_array.size)

    x = port.get_grid_x(var_name)
    y = port.get_grid_y(var_name)

    return StructuredField(x, y, shape)


def _construct_port_as_unstructured_field(port, var_name):
    x = port.get_grid_x(var_name)
    y = port.get_grid_y(var_name)
    c = port.get_grid_connectivity(var_name)
    o = port.get_grid_offset(var_name)

    return UnstructuredField(x, y, c, o)


def _construct_port_as_field(port, var_name):
    data_array = port.get_grid_values(var_name)
    if data_array is None:
        raise ValueError(var_name)

    if is_rectilinear_port(port, var_name):
        field = _construct_port_as_rectilinear_field(port, var_name,
                                                     data_array)
    elif is_structured_port(port, var_name):
        field = _construct_port_as_structured_field(port, var_name, data_array)
    else:
        field = _construct_port_as_unstructured_field(port, var_name)

    field.add_field(var_name, data_array,
                    centering=get_data_centering(field, data_array))

    return field


def get_data_centering(field, data_array):
    if data_is_centered_on_points(field, data_array):
        centering = 'point'
    elif data_is_centered_on_cells(field, data_array):
        centering = 'zonal'
    else:
        raise RuntimeError('statement should not be reached')
    return centering


def mesh_size_has_changed(field, data):
    return data.size not in [field.get_point_count(), field.get_cell_count()]


def data_is_centered_on_points(field, data):
    return data.size == field.get_point_count()


def data_is_centered_on_cells(field, data):
    return data.size == field.get_cell_count()


def _reconstruct_port_as_field (port, field):
    for var_name in field.keys():
        data_array = port.get_grid_values(var_name)

        if mesh_size_has_changed(field, data_array):
            field = _construct_port_as_field(port, var_name)
        else:
            field.add_field(var_name, data_array,
                            centering=get_data_centering(field, data_array))

    return field


_FORMAT_EXTENSION = {
    'nc': '.nc',
    'vtk': '.vtu',
    'bov': '.bov'
}


def normalize_format_name(fmt):
    if fmt.startswith('.'):
        fmt = fmt[1:]
    return fmt.lower()


def format_to_file_extension(fmt):
    try:
        return _FORMAT_EXTENSION[normalize_format_name(fmt)]
    except KeyError:
        raise BadFileFormatError(normalize_format_name(fmt))


def _file_name_lacks_extension(file_name):
    (_, ext) = os.path.splitext(file_name)
    return len(ext) <= 1


def construct_file_name(var_name, template='${var}', fmt=None, prefix=''):
    file_template = string.Template(template)
    file_name = file_template.safe_substitute(var=var_name)

    if _file_name_lacks_extension(file_name):
        file_ext = format_to_file_extension(fmt)
        file_name = file_name + file_ext

    return os.path.join(prefix, file_name)


def next_unique_file_name(file_name):
    (base, ext) = os.path.splitext(file_name)
    count = 0
    while os.path.isfile(file_name):
        file_name = base + '.%d' % count + ext
        count += 1
    return file_name
