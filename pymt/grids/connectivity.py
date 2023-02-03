"""
>>> get_connectivity((6, ))
array([0, 1, 1, 2, 2, 3, 3, 4, 4, 5])

>>> get_connectivity((6, ), ordering='ccw')
array([1, 0, 2, 1, 3, 2, 4, 3, 5, 4])

>>> get_connectivity((3, 4))
array([ 0,  1,  5,  4,  1,  2,  6,  5,  2,  3,  7,  6,  4,  5,  9,  8,  5,
        6, 10,  9,  6,  7, 11, 10])

>>> get_connectivity((3, 4), ordering='ccw')
array([ 1,  0,  4,  5,  2,  1,  5,  6,  3,  2,  6,  7,  5,  4,  8,  9,  6,
        5,  9, 10,  7,  6, 10, 11])

>>> shape = np.array([3, 4, 4])
>>> (c, o) = get_connectivity(shape, with_offsets=True)

>>> len(c) == (shape - 1).prod() * 8
True
>>> len(o) == (shape - 1).prod()
True
>>> np.all(np.diff(o) == 8)
True

>>> c[:o[0]]
array([ 0,  1,  5,  4, 16, 17, 21, 20])
>>> c[o[-2]:o[-1]]
array([26, 27, 31, 30, 42, 43, 47, 46])

>>> ids = get_connectivity((3, 4, 4), ordering='ccw')
>>> ids[:8]
array([ 1,  0,  4,  5, 17, 16, 20, 21])
>>> ids[-8:]
array([27, 26, 30, 31, 43, 42, 46, 47])

"""

import numpy as np


def _get_interior_ids(shape, dtype=int):
    """
    Get indices to the interior nodes of a structured grid. These are
    essentially the upper-left corners of cells formed by the points.
    For a 1D grid this is the left node of each line segment. For a
    3D grid this is the upper-left corner of the closest face of each
    cube.

    >>> _get_interior_ids((6, ))
    array([0, 1, 2, 3, 4])
    >>> _get_interior_ids((3, 4))
    array([0, 1, 2, 4, 5, 6])
    >>> _get_interior_ids((2, 3, 4))
    array([0, 1, 2, 4, 5, 6])
    >>> _get_interior_ids((3, 3, 4))
    array([ 0,  1,  2,  4,  5,  6, 12, 13, 14, 16, 17, 18])
    """
    i = np.arange(np.prod(shape), dtype=dtype)
    i.shape = shape
    obj = []
    for d in shape:
        obj.append(slice(0, d - 1))
    return i[tuple(obj)].flatten()


def _get_offsets(shape, ordering="cw", dtype=int):
    """
    >>> _get_offsets((16, ))
    array([0, 1])
    >>> _get_offsets((3, 4))
    array([0, 1, 5, 4])
    >>> _get_offsets((3, 4, 4))
    array([ 0,  1,  5,  4, 16, 17, 21, 20])

    >>> _get_offsets((16, ), ordering='ccw')
    array([1, 0])
    >>> _get_offsets((3, 4), ordering='ccw')
    array([1, 0, 4, 5])
    >>> _get_offsets((3, 4, 4), ordering='ccw')
    array([ 1,  0,  4,  5, 17, 16, 20, 21])
    """

    if ordering not in ["cw", "ccw", "none"]:
        raise TypeError(
            "Ordering value not understood (known values are 'cw', 'ccw' and 'none')"
        )
    if ordering == "none":
        ordered = False
    else:
        ordered = True

    if ordering == "ccw":
        offsets = np.array([1, 0], dtype=dtype)
    else:
        offsets = np.array([0, 1], dtype=dtype)

    strides = np.cumprod(list(shape[-1:0:-1]))
    for dim, stride in enumerate(strides):
        new_offsets = offsets + stride
        if ordered and dim % 2 == 0:
            offsets = np.append(offsets, new_offsets[::-1])
        else:
            offsets = np.append(offsets, new_offsets)

    return offsets


def get_connectivity(shape, **kwds):
    """
    Get the connectivity (and, optionally, offset) array for an ND structured
    grid. Elements will consist of two points for 1D grids, four points for
    2D grids, eight points for 3D grids, etc. For a uniform rectilinear grid
    this would be lines, squares, and cubes.

    The nodes of an element can be ordered either clockwise or counter-clockwise.

    Parameters
    ----------
    shape: tuple of int
        The shape of the grid.
    ordering: {'cw', 'ccw', 'none'}, optional
        Node ordering.  One of 'cw' (clockwise), 'ccw' (counter-clockwise),
        or 'none' (ordering not guaranteed).
    dtype: str or numpy.dtype
        The desired data type of the returned arrays.
    with_offsets: bool
        Return offset array along with connectivity

    Returns
    -------
    ndarray of int
        Array of connectivities. If with_offsets keyword is True, return a
        tuple of (connectivity, offset).


    Examples
    --------

    A 1D grid with three points has 2 elements.

    >>> get_connectivity ((3, ))
    array([0, 1, 1, 2])
    >>> get_connectivity ((3, ), ordering='ccw')
    array([1, 0, 2, 1])


    A 2D grid with 3 rows and 4 columns of nodes::

        ( 0 ) --- ( 1 ) --- ( 2 ) --- ( 3 )
          |         |         |         |
          |    0    |    1    |    2    |
          |         |         |         |
        ( 4 ) --- ( 5 ) --- ( 6 ) --- ( 7 )
          |         |         |         |
          |    3    |    4    |    5    |
          |         |         |         |
        ( 8 ) --- ( 9 ) --- ( 10) --- ( 11)

    >>> get_connectivity((3, 4))
    array([ 0,  1,  5,  4,  1,  2,  6,  5,  2,  3,  7,  6,  4,  5,  9,  8,  5,
            6, 10,  9,  6,  7, 11, 10])

    >>> get_connectivity((3, 4), ordering='ccw')
    array([ 1,  0,  4,  5,  2,  1,  5,  6,  3,  2,  6,  7,  5,  4,  8,  9,  6,
            5,  9, 10,  7,  6, 10, 11])

    If ordering doesn't matter, set ordering to 'none' as this could be slightly faster.

    >>> (ids, offsets) = get_connectivity((3, 4), ordering='none', with_offsets=True)
    >>> offsets
    array([ 4,  8, 12, 16, 20, 24])
    >>> ids
    array([ 0,  1,  4,  5,  1,  2,  5,  6,  2,  3,  6,  7,  4,  5,  8,  9,  5,
            6,  9, 10,  6,  7, 10, 11])

    Nodes connected to the first cell,

    >>> ids[:offsets[0]]
    array([0, 1, 4, 5])

    Nodes connected to the second cell,

    >>> ids[offsets[0]:offsets[1]]
    array([1, 2, 5, 6])

    Instead of using an offset array to indicate the end of each cell,
    you can return a list of connectivity arrays for each cell.

    >>> shape = np.array((3, 4))
    >>> ids = get_connectivity(shape, ordering='cw', as_cell_list=True)
    >>> len(ids) == (shape - 1).prod()
    True
    >>> ids # doctest: +NORMALIZE_WHITESPACE
    [array([0, 1, 5, 4]),
     array([1, 2, 6, 5]),
     array([2, 3, 7, 6]),
     array([4, 5, 9, 8]),
     array([ 5,  6, 10,  9]),
     array([ 6,  7, 11, 10])]
    """
    kwds.setdefault("dtype", int)
    kwds.setdefault("ordering", "cw")
    with_offsets = kwds.pop("with_offsets", False)
    as_cell_list = kwds.pop("as_cell_list", False)

    if with_offsets and as_cell_list:
        raise ValueError("with_offsets and as_cell_list keywords cannot both be True")

    c0 = _get_interior_ids(shape, dtype=kwds["dtype"])
    offsets = _get_offsets(shape, **kwds)
    points_per_cell = len(offsets)

    if as_cell_list:
        offset_list = []
        for offset in offsets:
            offset_list.append(c0 + offset)
        c = []
        for cell in zip(*offset_list):
            c.append(np.array(cell, dtype=kwds["dtype"]))
    else:
        c = np.empty((c0.size * points_per_cell,), dtype=kwds["dtype"])
        for i, offset in enumerate(offsets):
            c[i::points_per_cell] = c0 + offset

    if with_offsets:
        o = np.arange(points_per_cell, len(c) + 1, points_per_cell, dtype=kwds["dtype"])
        return (c, o)
    else:
        return c


def get_connectivity_2d(shape, ordering="cw", dtype=int):
    """This is a little slower than the above and less general.

    Examples
    --------
    >>> get_connectivity_2d((3, 4))
    array([ 0,  1,  5,  4,  1,  2,  6,  5,  2,  3,  7,  6,  4,  5,  9,  8,  5,
            6, 10,  9,  6,  7, 11, 10])
    """
    if len(shape) != 2:
        raise ValueError("number of dimensions must be 2")

    point_count = shape[0] * shape[1]

    point_ids = np.arange(point_count, dtype=dtype)
    point_ids.shape = shape

    c_ul = point_ids[:-1, :-1].flatten()
    c_ur = point_ids[:-1, 1:].flatten()
    c_lr = point_ids[1:, 1:].flatten()
    c_ll = point_ids[1:, :-1].flatten()

    c = np.empty((4 * c_ul.size,), dtype=c_ul.dtype)
    if ordering == "cw":
        c[::4] = c_ul
        c[1::4] = c_ur
        c[2::4] = c_lr
        c[3::4] = c_ll
    else:
        c[::4] = c_ur
        c[1::4] = c_ul
        c[2::4] = c_ll
        c[3::4] = c_lr

    return c


def get_connectivity_1d(shape, ordering="cw", dtype=int):
    if len(shape) != 1:
        raise ValueError("number of dimensions must be 1")

    point_count = shape[0]

    point_ids = np.arange(point_count, dtype=dtype)

    c_left = point_ids[:-1]
    c_right = point_ids[1:]

    c = np.empty((4 * c_left.size,), dtype=c_left.dtype)
    if ordering == "cw":
        c[::2] = c_left
        c[1::2] = c_right
    else:
        c[::2] = c_right
        c[1::2] = c_left

    return c


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
