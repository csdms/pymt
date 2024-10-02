"""
Notes
-----
This function supports both indexing conventions through the indexing keyword
argument.  Giving the string 'ij' returns a meshgrid with matrix indexing,
while 'xy' returns a meshgrid with Cartesian indexing.  In the 2-D case
with inputs of length M and N, the outputs are of shape (N, M) for 'xy'
indexing and (M, N) for 'ij' indexing.  In the 3-D case with inputs of
length M, N and P, outputs are of shape (N, M, P) for 'xy' indexing and (M,
N, P) for 'ij' indexing.  The difference is illustrated by the following
code snippet::

        xv, yv = meshgrid(x, y, sparse=False, indexing='ij')
        for i in range(nx):
            for j in range(ny):
                # treat xv[i,j], yv[i,j]

        xv, yv = meshgrid(x, y, sparse=False, indexing='xy')
        for i in range(nx):
            for j in range(ny):
                # treat xv[j,i], yv[j,i]

See Also
--------
index_tricks.mgrid : Construct a multi-dimensional "meshgrid"
                     using indexing notation.
index_tricks.ogrid : Construct an open multi-dimensional "meshgrid"
                     using indexing notation.

Examples
--------

>>> nx, ny = (3, 2)
>>> x = np.linspace(0, 1, nx)
>>> y = np.linspace(0, 1, ny)
>>> xv, yv = meshgrid(x, y)
>>> xv
array([[0. , 0.5, 1. ],
       [0. , 0.5, 1. ]])
>>> yv
array([[0., 0., 0.],
       [1., 1., 1.]])
>>> xv, yv = meshgrid(x, y, sparse=True)  # make sparse output arrays
>>> xv
array([[0. , 0.5, 1. ]])
>>> yv
array([[0.],
       [1.]])

`meshgrid` is very useful to evaluate functions on a grid.

>>> x = np.arange(-5, 5, 0.1)
>>> y = np.arange(-5, 5, 0.1)
>>> xx, yy = meshgrid(x, y, sparse=True)
>>> z = np.sin(xx**2 + yy**2) / (xx**2 + yy**2)
"""

import numpy as np


# Based on scitools meshgrid
def meshgrid(*xi, **kwargs):
    """Coordinate matrices from two or more coordinate vectors.

    Make N-D coordinate arrays for vectorized evaluations of
    N-D scalar/vector fields over N-D grids, given
    one-dimensional coordinate arrays x1, x2,..., xn.

    Parameters
    ----------
    xi: array_like
            1-D arrays representing the coordinates of a grid.
    indexing: {'xy', 'ij'}, optional
        Cartesian ('xy', default) or matrix ('ij') indexing of output.
        See Notes for more details.
    sparse: bool, optional
        If True a sparse grid is returned in order to conserve memory.
        Default is False.
    copy: bool, optional
        If False, a view into the original arrays are returned in
        order to conserve memory.  Default is True.  Please note that
        ``sparse=False, copy=False`` will likely return non-contiguous arrays.
        Furthermore, more than one element of a broadcast array may refer to
        a single memory location.  If you need to write to the arrays, make
        copies first.

    Returns
    -------
    ndarray
        For vectors `x1`, `x2`,..., 'xn' with lengths ``Ni=len(xi)`` ,
        return ``(N1, N2, N3,...Nn)`` shaped arrays if indexing='ij'
        or ``(N2, N1, N3,...Nn)`` shaped arrays if indexing='xy'
        with the elements of `xi` repeated to fill the matrix along
        the first dimension for `x1`, the second for `x2` and so on.

    """
    if len(xi) < 2:
        msg = "meshgrid() takes 2 or more arguments (%d given)" % int(len(xi) > 0)
        raise ValueError(msg)

    args = np.atleast_1d(*xi)
    ndim = len(args)

    copy_ = kwargs.get("copy", True)
    sparse = kwargs.get("sparse", False)
    indexing = kwargs.get("indexing", "xy")
    if indexing not in ["xy", "ij"]:
        raise ValueError("Valid values for `indexing` are 'xy' and 'ij'.")

    s0 = (1,) * ndim
    output = [x.reshape(s0[:i] + (-1,) + s0[i + 1 : :]) for i, x in enumerate(args)]

    shape = [x.size for x in output]

    if indexing == "xy":
        # switch first and second axis
        output[0].shape = (1, -1) + (1,) * (ndim - 2)
        output[1].shape = (-1, 1) + (1,) * (ndim - 2)
        shape[0], shape[1] = shape[1], shape[0]

    if sparse:
        if copy_:
            return [x.copy() for x in output]
        else:
            return output
    else:
        # Return the full N-D matrix (not only the 1-D vector)
        if copy_:
            mult_fact = np.ones(shape, dtype=int)
            return [x * mult_fact for x in output]
        else:
            return np.broadcast_arrays(*output)


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
