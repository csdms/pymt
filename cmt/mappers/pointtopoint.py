#! /bin/env python

import numpy as np
from scipy.spatial import KDTree
from .imapper import IGridMapper, IncompatibleGridError
#from .mapper import IncompatibleGridError


def _flat_view(array):
    return array.view().reshape((array.size, ))


def copy_good_values(src, dst, bad_val=-999):
    assert(src.size == dst.size)

    flat_src, flat_dst = _flat_view(src), _flat_view(dst)

    ids_to_copy = flat_src > bad_val
    flat_dst[ids_to_copy] = flat_src[ids_to_copy]


class NearestVal(IGridMapper):
    def initialize(self, dest_grid, src_grid, var_names=None):
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
        if var_names is None:
            var_names = []

        if not self.test(dest_grid, src_grid):
            raise IncompatibleGridError(dest_grid.name, src_grid.name)

        assert(len(var_names) <= 1)

        if len(var_names) == 0:
            (x, y) = src_grid.get_x().flat, src_grid.get_y().flat
        else:
            dst_name, src_name = var_names[0]
            (x, y) = (src_grid.get_x(src_name).flat,
                      src_grid.get_y(src_name).flat)

        tree = KDTree(zip(x, y))

        if len(var_names) == 0:
            (x, y) = dest_grid.get_x().flat, dest_grid.get_y().flat
        else:
            dst_name, src_name = var_names[0]
            (x, y) = (dest_grid.get_x(dst_name).flat,
                      dest_grid.get_y(dst_name).flat)

        (_, self._nearest_src_id) = tree.query(zip(x, y))

        #(_, self._nearest_src_id) = tree.query(
        #    zip(dest_grid.get_x(dst_name).flat,
        #        dest_grid.get_y(dst_name).flat))

    def run(self, src_values, dest_values=None):
        if dest_values is None:
            dest_values = np.zeros(len(self._nearest_src_id),
                                   dtype=src_values.dtype)
        elif not isinstance(dest_values, np.ndarray):
            raise TypeError('Destination array must be a numpy array')

        copy_good_values(src_values.flat[self._nearest_src_id],
                         dest_values, bad_val=-999)

        return dest_values

    def test(self, dst_grid, src_grid):
        return dst_grid is not None and src_grid is not None

    def name(self):
        return 'PointToPoint'


class _NearestVal(IGridMapper):
    def initialize(self, dest_grid, src_grid):
        if not self.test(dest_grid, src_grid):
            raise IncompatibleGridError(dest_grid.name, src_grid.name)

        try:
            tree = KDTree(zip(src_grid.get_x(), src_grid.get_y()))
        except AttributeError:
            tree = KDTree(zip(src_grid.get_grid_x(), src_grid.get_grid_y()))
        try:
            (_, self._nearest_src_id) = tree.query(zip(dest_grid.get_x(),
                                                       dest_grid.get_y()))
        except AttributeError:
            (_, self._nearest_src_id) = tree.query(zip(dest_grid.get_grid_x(),
                                                       dest_grid.get_grid_y()))

    def run(self, src_values, dest_values=None):
        if dest_values is None:
            dest_values = np.zeros(len(self._nearest_src_id),
                                   dtype=src_values.dtype)
        elif not isinstance(dest_values, np.ndarray):
            raise TypeError('Destination array must be a numpy array')

        copy_good_values(src_values.flat[self._nearest_src_id],
                         dest_values, bad_val=-999)

        return dest_values

    def test(self, dst_grid, src_grid):
        return dst_grid is not None and src_grid is not None

    def name(self):
        return 'PointToPoint'


if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
