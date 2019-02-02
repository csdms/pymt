from __future__ import print_function

import numpy as np
from six.moves import xrange

from pymt.grids.connectivity import get_connectivity


def raster_node_coordinates(shape, spacing=None, origin=None):
    """Node coordinates of a uniform rectilinear grid.

    Parameters
    ----------
    shape : array_like
        Size of grid in each dimension.
    spacing : array_like (optional)
        Node spacing in each dimension (default is unit spacing).
    origin : array_like (optional)
        Coordinates of the origin node (default is 0.0).

    Returns
    -------
    coords : ndarray
        Node coordinates.

    Examples
    --------
    >>> from pymt.component.grid import raster_node_coordinates
    >>> (y, x) = raster_node_coordinates((2, 3))
    >>> y
    array([[ 0.,  0.,  0.],
           [ 1.,  1.,  1.]])
    >>> x
    array([[ 0.,  1.,  2.],
           [ 0.,  1.,  2.]])

    >>> (x, ) = raster_node_coordinates((3, ), (2., ), (1., ))
    >>> x
    array([ 1.,  3.,  5.])
    """
    spacing = spacing or np.ones_like(shape, dtype=float)
    origin = origin or np.zeros_like(shape, dtype=float)

    coordinate_vectors = []
    for shape_, spacing_, origin_ in zip(shape, spacing, origin):
        start, stop = origin_, origin_ + shape_ * spacing_
        coordinate_vectors.append(np.arange(start, stop, spacing_))

    return np.meshgrid(*coordinate_vectors, indexing="ij")


def get_raster_node_coordinates(grid, grid_id):
    """Get coordinates of nodes on a raster grid.

    Parameters
    ----------
    grid : grid_like
        A raster grid.
    grid_id : int
        Grid identifier.

    Returns
    -------
    coords : ndarray
        Coordinates of the grid nodes.

    Examples
    --------
    >>> from pymt.component.grid import get_raster_node_coordinates
    >>> class RasterGrid(object):
    ...     def get_grid_shape(self, grid_id):
    ...         return (2, 3)
    ...     def get_grid_spacing(self, grid_id):
    ...         return (1., 2.)
    ...     def get_grid_origin(self, grid_id):
    ...         return (2., 1.)
    >>> g = RasterGrid()
    >>> (y, x) = get_raster_node_coordinates(g, 0)
    >>> y
    array([[ 2.,  2.,  2.],
           [ 3.,  3.,  3.]])
    >>> x
    array([[ 1.,  3.,  5.],
           [ 1.,  3.,  5.]])
    """
    (shape, spacing, origin) = (
        grid.get_grid_shape(grid_id),
        grid.get_grid_spacing(grid_id),
        grid.get_grid_origin(grid_id),
    )

    return raster_node_coordinates(shape, spacing=spacing, origin=origin)


def get_rectilinear_node_coordinates(grid, grid_id):
    """Get coordinates of nodes on a rectilinear grid.

    Parameters
    ----------
    grid: grid_like
        A rectilinear grid.
    grid_id : int
        Grid identifier.

    Returns
    -------
    coords : ndarray
        Coordinates of the grid nodes.

    Examples
    --------
    >>> from pymt.component.grid import get_rectilinear_node_coordinates
    >>> class RectilinearGrid(object):
    ...     def get_grid_x(self, grid_id):
    ...         return (0., 3., 4)
    ...     def get_grid_y(self, grid_id):
    ...         return (2., 7.)
    >>> g = RectilinearGrid()
    >>> (y, x) = get_rectilinear_node_coordinates(g, 0)
    >>> y
    array([[ 2.,  2.,  2.],
           [ 7.,  7.,  7.]])
    >>> x
    array([[ 0.,  3.,  4.],
           [ 0.,  3.,  4.]])
    """
    coordinate_vectors = []
    for coordinate_name in ["z", "y", "x"]:
        try:
            func = getattr(grid, "get_grid_" + coordinate_name)
            coordinate_vectors.append(func(grid_id))
        except (AttributeError, NotImplementedError):
            pass

    return np.meshgrid(*coordinate_vectors, indexing="ij")


def get_structured_node_coordinates(grid, grid_id):
    """Get coordinates of nodes on a structured grid.

    Parameters
    ----------
    grid: grid_like
        A structured grid.
    grid_id : int
        Grid identifier.

    Returns
    -------
    coords : ndarray
        Coordinates of the grid nodes.

    Examples
    --------
    >>> from pymt.component.grid import get_structured_node_coordinates
    >>> class StructuredGrid(object):
    ...     def get_grid_x(self, grid_id):
    ...         return np.array((0., 3., 4, 0., 3., 4.)).reshape((2, 3))
    ...     def get_grid_y(self, grid_id):
    ...         return np.array((2., 2., 2., 7., 7., 7.)).reshape((2, 3))
    ...     def get_grid_z(self, grid_id):
    ...         raise NotImplementedError('get_grid_z')
    >>> g = StructuredGrid()
    >>> (y, x) = get_structured_node_coordinates(g, 0)
    >>> y
    array([[ 2.,  2.,  2.],
           [ 7.,  7.,  7.]])
    >>> x
    array([[ 0.,  3.,  4.],
           [ 0.,  3.,  4.]])
    """
    node_coordinates = []
    for coordinate_name in ["z", "y", "x"]:
        try:
            func = getattr(grid, "get_grid_" + coordinate_name)
            node_coordinates.append(np.array(func(grid_id)))
        except (AttributeError, NotImplementedError):
            pass
    return node_coordinates


def get_structured_node_connectivity(grid, grid_id):
    """Get cell connectivity on a structured grid of quadrilaterals.

    Parameters
    ----------
    grid: grid_like
        A structured grid.
    grid_id : int
        Grid identifier.

    Returns
    -------
    conn : ndarray
        Connectivities of nodes to cells.

    Examples
    --------
    >>> from pymt.component.grid import get_structured_node_connectivity
    >>> class StructuredGrid(object):
    ...     def get_grid_shape(self, grid_id):
    ...         return (2, 3)
    >>> g = StructuredGrid()
    >>> (c, o) = get_structured_node_connectivity(g, 0)
    >>> c
    array([0, 1, 4, 3, 1, 2, 5, 4])
    >>> o
    array([4, 8])
    """
    shape = grid.get_grid_shape(grid_id)
    return get_connectivity(shape, with_offsets=True)


class GridMixIn(object):
    """Mix-in that makes a Component grid-like.

    Examples
    --------
    >>> class Port(object):
    ...     def get_component_name(self):
    ...         return 'test-component'
    ...     def get_input_item_count(self):
    ...         return 1
    ...     def get_input_item_list(self):
    ...         return ['invar']
    ...     def get_output_item_count(self):
    ...         return 1
    ...     def get_output_item_list(self):
    ...         return ['outvar']
    ...     def get_grid_shape(self, grid_id):
    ...         return (2, 3)
    ...     def get_grid_spacing(self, grid_id):
    ...         return (2., 1.)
    ...     def get_grid_origin(self, grid_id):
    ...         return (0., 0.)

    >>> from pymt.component.grid import GridMixIn
    >>> class Component(GridMixIn):
    ...     def __init__(self):
    ...         self._port = Port()
    ...         super(Component, self).__init__()
    >>> c = Component()
    >>> c.name
    'test-component'
    >>> c.input_items
    ['invar']
    >>> c.output_items
    ['outvar']
    >>> c.get_grid_type(0)
    'RASTER'
    >>> c.get_x(0)
    array([[ 0.,  1.,  2.],
           [ 0.,  1.,  2.]])
    >>> c.get_y(0)
    array([[ 0.,  0.,  0.],
           [ 2.,  2.,  2.]])
    """

    def __init__(self):
        self._coords = {}
        self._connectivity = {}
        self._grid_type = {}

    @property
    def name(self):
        """Name of the wrapped component.
        """
        return self._port.get_component_name()

    @property
    def input_items(self):
        """Input item names as a list.
        """
        if self._port.get_input_item_count() > 0:
            return self._port.get_input_item_list()
        else:
            return []

    @property
    def output_items(self):
        """Output item names as a list.
        """
        if self._port.get_output_item_count() > 0:
            return self._port.get_output_item_list()
        else:
            return []

    def _set_grid_type(self, grid_id):
        try:
            shape = self._port.get_grid_shape(grid_id)
            if shape is None:
                raise Exception
        except Exception:
            grid_type = "UNSTRUCTURED"
        else:
            try:
                self._port.get_grid_spacing(grid_id)
            except Exception:
                x = self._port.get_grid_x(grid_id)
                if len(x) == shape[-1]:
                    grid_type = "RECTILINEAR"
                else:
                    grid_type = "STRUCTURED"
            else:
                grid_type = "RASTER"
        self._grid_type[grid_id] = grid_type

    def get_grid_type(self, grid_id):
        """The type of the grid.

        Parameters
        ----------
        grid_id : int
            Grid identifier.

        Returns
        -------
        type : str
            The type of the grid.
        """
        try:
            return self._grid_type[grid_id]
        except (AttributeError, KeyError):
            self._set_grid_type(grid_id)
            return self._grid_type[grid_id]

    def _set_coords(self, grid_id):
        grid_type = self.get_grid_type(grid_id)

        if grid_type == "RASTER":
            coords = get_raster_node_coordinates(self._port, grid_id)
        elif grid_type == "RECTILINEAR":
            coords = get_rectilinear_node_coordinates(self._port, grid_id)
        else:
            coords = get_structured_node_coordinates(self._port, grid_id)

        self._coords[grid_id] = coords

    def _get_coord_by_dim(self, grid_id, dim):
        try:
            return self._coords[grid_id][dim]
        except (AttributeError, KeyError):
            self._set_coords(grid_id)
            return self._coords[grid_id][dim]
        except IndexError:
            print(self._port)
            print(grid_id)
            print(self._coords)
            raise

    def _set_connectivity(self, grid_id):
        grid_type = self.get_grid_type(grid_id)
        if grid_type != "UNSTRUCTURED":
            (connectivity, offset) = get_structured_node_connectivity(
                self._port, grid_id
            )
        else:
            (connectivity, offset) = (
                self.get_grid_connectivity(grid_id),
                self.get_grid_offset(grid_id),
            )

        self._connectivity[grid_id] = (connectivity, offset)

    def _get_connectivity(self, grid_id):
        try:
            return self._connectivity[grid_id][0]
        except (AttributeError, KeyError):
            self._set_connectivity(grid_id)
            return self._connectivity[grid_id][0]

    def _get_offset(self, grid_id):
        try:
            return self._connectivity[grid_id][1]
        except (AttributeError, KeyError):
            self._set_connectivity(grid_id)
            return self._connectivity[grid_id][1]

    def get_x(self, grid_id):
        return self._get_coord_by_dim(grid_id, -1)

    def get_y(self, grid_id):
        return self._get_coord_by_dim(grid_id, -2)

    def get_z(self, grid_id):
        return self._get_coord_by_dim(grid_id, -3)

    def get_connectivity(self, grid_id):
        return self._get_connectivity(grid_id)

    def get_offset(self, grid_id):
        return self._get_offset(grid_id)

    def get_value(self, *args, **kwds):
        return self._port.get_value(*args, **kwds)

    def set_value(self, name, values):
        return self._port.set_value(name, values)

    def get_var_units(self, name):
        return self._port.get_var_units(name)
