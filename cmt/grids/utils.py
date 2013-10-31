import numpy as np


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
