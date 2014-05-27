import numpy as np

from cmt.grids.connectivity import get_connectivity


def get_raster_node_coordinates(grid, name):
    (shape, spacing, origin) = (grid.get_grid_shape(name),
                                grid.get_grid_spacing(name),
                                grid.get_grid_origin(name))

    coordinate_vectors = []
    for dim in xrange(len(shape)):
        coordinate_vectors.append(np.arange(
            origin[dim], origin[dim] + shape[dim] * spacing[dim], spacing[dim]))
    
    return np.meshgrid(*coordinate_vectors, indexing='ij')


def get_rectlinear_node_coordinates(grid, name):
    coordinate_vectors = []
    for coordinate_name in ['z', 'y', 'z']:
        func = getattr(grid, 'get_grid_' + coordinate_name)
        try:
            coordinate_vectors.append(func(name))
        except Exception:
            pass

    return np.meshgrid(*coordinate_vectors, indexing='ij')


def get_structured_node_coordinates(grid, name):
    node_coordinates = []
    for coordinate_name in ['z', 'y', 'x']:
        func = getattr(grid, 'get_grid_' + coordinate_name)
        try:
            node_coordinates.append(func(name))
        except Exception:
            pass
    return node_coordinates


def get_structured_node_connectivity(grid, name):
    shape = grid.get_grid_shape(name)
    return get_connectivity(shape, with_offsets=True)


class GridMixIn(object):
    def __init__(self):
        self._coords = {}
        self._connectivity = {}
        self._grid_type = {}

    @property
    def name(self):
        return self._port.get_component_name()

    @property
    def input_items(self):
        if self._port.get_input_item_count() > 0:
            return self._port.get_input_item_list()
        else:
            return []

    @property
    def output_items(self):
        if self._port.get_output_item_count() > 0:
            return self._port.get_output_item_list()
        else:
            return []

    def _set_grid_type(self, var_name):
        try:
            shape = self._port.get_grid_shape(var_name)
            if shape is None:
                raise Exception
        except Exception:
            grid_type = 'UNSTRUCTURED'
        else:
            try:
                self._port.get_grid_spacing(var_name)
            except Exception:
                x = self._port.get_grid_x(var_name)
                if len(x) == shape[-1]:
                    grid_type = 'RECTILINEAR'
                else:
                    grid_type = 'STRUCTURED'
            else:
                grid_type = 'RASTER'
        self._grid_type[var_name] = grid_type

    def get_grid_type(self, var_name):
        try:
            return self._grid_type[var_name]
        except (AttributeError, KeyError):
            self._set_grid_type(var_name)
            return self._grid_type[var_name]

    def _set_coords(self, var_name):
        grid_type = self.get_grid_type(var_name)

        if grid_type == 'RASTER':
            coords = get_raster_node_coordinates(self._port, var_name)
        elif grid_type == 'RECTILINEAR':
            coords = get_rectilinear_node_coordinates(self._port, var_name)
        else:
            coords = get_structured_node_coordinates(self._port, var_name)

        self._coords[var_name] = coords

    def _get_coord_by_dim(self, var_name, dim):
        try:
            return self._coords[var_name][dim]
        except (AttributeError, KeyError):
            self._set_coords(var_name)
            return self._coords[var_name][dim]
        except IndexError:
            print self._port
            print var_name
            print self._coords
            raise

    def _set_connectivity(self, var_name):
        grid_type = self.get_grid_type(var_name)

        if grid_type != 'UNSTRUCTURED':
            coords = get_raster_node_coordinate(self._port, var_name)
        else:
            (connectivity, offset) = (self.get_grid_connectivity(var_name),
                                      self.get_grid_offset(var_name))

        self._connectivity[var_name] = (connectivity, offset)

    def _get_connectivity(self, name):
        try:
            return self._connectivity[var_name][0]
        except (AttributeError, KeyError):
            self._set_connectivity(var_name)
            return self._connectivity[var_name][0]

    def _get_offset(self, name):
        try:
            return self._connectivity[var_name][1]
        except (AttributeError, KeyError):
            self._set_connectivity(var_name)
            return self._connectivity[var_name][1]

    def get_x(self, var_name):
        return self._get_coord_by_dim(var_name, -1)

    def get_y(self, var_name):
        return self._get_coord_by_dim(var_name, -2)

    def get_z(self, var_name):
        return self._get_coord_by_dim(var_name, -3)

    def get_connectivity(self, var_name):
        return self._get_connectivity(var_name)

    def get_offset(self, var_name):
        return self._get_offset(var_name)

    def get_grid_values(self, *args, **kwds):
        return self._port.get_grid_values(*args, **kwds)

    def set_grid_values(self, name, values):
        return self._port.set_grid_values(name, values)

