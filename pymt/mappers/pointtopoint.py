import numpy as np
from scipy.spatial import KDTree

from .imapper import IGridMapper, IncompatibleGridError

# from .mapper import IncompatibleGridError


def _flat_view(array):
    return array.view().reshape((array.size,))


def copy_good_values(src, dst, bad_val=-999):
    """Copy only the good values from one array to another.

    Parameters
    ----------
    src : array_like
        Array of source values.
    dst : array_like
        Array into which to copy the good values.
    bad_val : float (optional)
        Value below which indicates a bad value.

    Returns
    -------
    dst : array_like
        The destination array.

    Examples
    --------
    >>> import numpy as np
    >>> from pymt.mappers.pointtopoint import copy_good_values
    >>> x = np.arange(6)
    >>> y = np.zeros((2, 3))
    >>> rv = copy_good_values(x, y)
    >>> rv is y
    True
    >>> y
    array([[ 0.,  1.,  2.],
           [ 3.,  4.,  5.]])
    >>> copy_good_values(x, np.zeros(6), bad_val=3.)
    array([ 0.,  0.,  0.,  0.,  4.,  5.])
    """
    if src.size != dst.size:
        raise ValueError("size mismatch between source and destination arrays")

    flat_src, flat_dst = _flat_view(src), _flat_view(dst)

    ids_to_copy = flat_src > bad_val
    flat_dst[ids_to_copy] = flat_src[ids_to_copy]

    return dst


class NearestVal(IGridMapper):
    """
    Examples
    --------
    >>> import numpy as np
    >>> from pymt.grids.map import RectilinearMap
    >>> from pymt.mappers.pointtopoint import NearestVal
    >>> src = RectilinearMap([0, 1, 2], [0, 2])
    >>> dst = RectilinearMap([.25, 1.25, 2.25], [.25, 1.25])
    >>> mapper = NearestVal()
    >>> mapper.initialize(dst, src)
    >>> mapper.run(np.arange(6.))
    array([ 0.,  1.,  2.,  3.,  4.,  5.])
    """

    _name = "PointToPoint"

    def initialize(self, dest_grid, src_grid, **kwds):
        """Map points on one grid to the nearest points on another.

        Parameters
        ----------
        dest_grid : grid_like
            Grid onto which points are mapped
        src_grid : grid_like
            Grid from which points are taken.
        var_names : iterable of tuples (optional)
            Iterable of (*dest*, *src*) variable names.
        """
        var_names = kwds.get("var_names", None)
        if var_names is None:
            var_names = []

        if len(var_names) > 1:
            raise ValueError("only 0 or 1 var_names allowed")

        if not NearestVal.test(dest_grid, src_grid):
            raise IncompatibleGridError(dest_grid.name, src_grid.name)

        if len(var_names) == 0:
            (x, y) = src_grid.get_x().flat, src_grid.get_y().flat
        else:
            dst_name, src_name = var_names[0]
            (x, y) = (src_grid.get_x(src_name).flat, src_grid.get_y(src_name).flat)

        tree = KDTree(list(zip(x, y)))

        if len(var_names) == 0:
            (x, y) = dest_grid.get_x().flat, dest_grid.get_y().flat
        else:
            dst_name, src_name = var_names[0]
            (x, y) = (dest_grid.get_x(dst_name).flat, dest_grid.get_y(dst_name).flat)

        (_, self._nearest_src_id) = tree.query(list(zip(x, y)))

    def run(self, src_values, **kwds):
        """Map source values onto destination values.

        Parameters
        ----------
        src_values : ndarray
            Source values at points.
        dst_vals : ndarray (optional)
            Destination array to put mapped values.

        Returns
        -------
        dest : ndarray
            The (possibly newly-created) destination array.
        """
        dst_vals = kwds.get("dst_vals", None)
        bad_val = kwds.get("bad_val", -999)

        if dst_vals is None:
            dst_vals = np.zeros(len(self._nearest_src_id), dtype=src_values.dtype)
        elif not isinstance(dst_vals, np.ndarray):
            raise TypeError("Destination array must be a numpy array")

        copy_good_values(
            src_values.flat[self._nearest_src_id], dst_vals, bad_val=bad_val
        )

        return dst_vals

    @staticmethod
    def test(dst_grid, src_grid):
        """Test if grids are compatible with this mapper.

        Parameters
        ----------
        dst_grid : grid_like
            Grid onto which points are mapped
        src_grid : grid_like
            Grid from which points are taken.
        """
        return dst_grid is not None and src_grid is not None

    @property
    def name(self):
        """Name of the grid mapper."""
        return self._name
