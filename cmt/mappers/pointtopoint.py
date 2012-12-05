#! /bin/env python

import numpy as np
from scipy.spatial import KDTree
from imapper import IGridMapper
from cmt.mappers import IncompatibleGridError

class NearestVal (IGridMapper):
    def initialize (self, dest_grid, src_grid):
        if not self.test (dest_grid, src_grid):
            raise IncompatibleGridError (dest_grid.name,
                                         src_grid.name)
        tree = KDTree (zip (src_grid.get_x (), src_grid.get_y ()))
        (self._l, self._i) = tree.query (zip (dest_grid.get_x (),
                                              dest_grid.get_y ()))

    def run (self, src_values, dest_values=None):
        if dest_values is None:
            dest_values = np.zeros (len (self._i))
        elif not isinstance (dest_values, np.ndarray):
            raise TypeError ('Destination array must be a numpy array')

        for (j, i) in enumerate (self._i):
            if src_values.flat[i]>-999:
                dest_values.flat[j] = src_values.flat[i]

        return dest_values

    def test (self, dst_grid, src_grid):
        #return (all (np.diff (dst_grid.get_offset ())==1) and
        #        all (np.diff (src_grid.get_offset ())==1))
        return True
    def name (self):
        return 'PointToPoint'

if __name__ == "__main__":
    import doctest
    doctest.testmod (optionflags=doctest.NORMALIZE_WHITESPACE)

