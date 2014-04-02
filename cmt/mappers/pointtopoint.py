#! /bin/env python

import numpy as np
from scipy.spatial import KDTree
from .imapper import IGridMapper, IncompatibleGridError


def _flat_view(array):
    return array.view().reshape((array.size, ))


def copy_good_values(src, dst, bad_val=-999):
    assert(src.size == dst.size)

    flat_src, flat_dst = _flat_view(src), _flat_view(dst)

    ids_to_copy = flat_src > bad_val
    flat_dst[ids_to_copy] = flat_src[ids_to_copy]


class NearestVal(IGridMapper):
    def initialize(self, dest_grid, src_grid):
        if not self.test(dest_grid, src_grid):
            raise IncompatibleGridError(dest_grid.name, src_grid.name)

        tree = KDTree(zip(src_grid.get_x(), src_grid.get_y()))
        (_, self._nearest_src_id) = tree.query(zip(dest_grid.get_x(),
                                                   dest_grid.get_y()))

    def run(self, src_values, dest_values=None):
        if dest_values is None:
            dest_values = np.zeros(len(self._nearest_src_id),
                                   dtype=src_values.dtype)
        elif not isinstance(dest_values, np.ndarray):
            raise TypeError('Destination array must be a numpy array')

        copy_good_values(src_values.flat[self._nearest_src_id],
                         dest_values, ignore=-999)

        return dest_values

    def test(self, dst_grid, src_grid):
        return True

    def name(self):
        return 'PointToPoint'


if __name__ == "__main__":
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)
