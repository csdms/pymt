import numpy as np


from cmt.grids.assertions import (is_rectilinear, is_structured,
                                  is_unstructured)


def get_default_coordinate_units(n_dims):
    if n_dims <= 0 or n_dims > 3:
        raise ValueError('dimension must be between one and three')
    return ['-'] * n_dims


def get_default_coordinate_names(n_dims):
    if n_dims <= 0 or n_dims > 3:
        raise ValueError('dimension must be between one and three')
    return ['z', 'y', 'x'][- n_dims:]


def assert_arrays_are_equal_size(*args):
    first_size = args[0].size
    for arg in args[1:]:
        if arg.size != first_size:
            raise AssertionError('arrays are not the same length')


def args_as_numpy_arrays(*args):
    np_arrays = []
    for arg in args:
        if isinstance(arg, np.ndarray):
            np_array = arg.view()
        else:
            np_array = np.array(arg)
        np_array.shape = (np_array.size, )
        np_arrays.append(np_array)
    return tuple(np_arrays)


def coordinates_to_numpy_matrix(*args):
    args = args_as_numpy_arrays(*args)
    assert_arrays_are_equal_size(*args)

    coords = np.empty((len(args), len(args[0])), dtype=np.float)
    for (dim, arg) in enumerate(args):
        coords[dim][:] = arg.flatten()
    return coords


def non_singleton_axes(grid):
    try:
        shape = grid.get_shape()
    except AttributeError:
        return np.arange(grid.get_dim_count())
    else:
        (indices, ) = np.where(shape > 1)
        return indices


def non_singleton_shape(grid):
    shape = grid.get_shape()
    (indices, ) = np.where(shape > 1)
    return shape[indices]


def non_singleton_coordinate_names(grid):
    indices = non_singleton_axes(grid)
    return grid.get_coordinate_name(indices)


def non_singleton_dimension_names(grid):
    if is_structured(grid, strict=False):
        coordinate_names = non_singleton_coordinate_names(grid)
        return np.array(['n' + name for name in coordinate_names])
    else:
        return np.array(['n_points'])


def non_singleton_dimension_shape(grid):
    if is_rectilinear(grid, strict=False):
        shape = non_singleton_dimension_names(grid)
        return shape[:, np.newaxis]
    elif is_structured(grid, strict=True):
        shape = non_singleton_dimension_names(grid)
        return np.tile(shape, (len(shape), 1))
    elif is_unstructured(grid, strict=True):
        shape = np.array(['n_points'])
        return np.tile(shape, (grid.get_dim_count(), 1))
