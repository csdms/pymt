#! /bin/env python

import numpy as np
from scipy.spatial import KDTree
from imapper import IGridMapper
from cmt.mappers import IncompatibleGridError


class CellToPoint(IGridMapper):
    def initialize(self, dest_grid, src_grid):
        if not self.test(dest_grid, src_grid):
            raise IncompatibleGridError(dest_grid.name,
                                        src_grid.name)
        dst_x = dest_grid.get_x()
        dst_y = dest_grid.get_y()

        tree = KDTree(zip(src_grid.get_x(), src_grid.get_y()))
        (self._l, self._i) = tree.query(zip(dst_x, dst_y))

        self._map = np.zeros(len(dst_x), dtype=np.int) - 1
        for (j, point_id) in zip(range(len(self._i)), self._i):
            for cell_id in src_grid.get_shared_cells(point_id):
                if src_grid.is_in_cell(dst_x[j], dst_y[j], cell_id):
                    self._map[j] = cell_id

        self._bad = self._map == -1

    def run(self, src_values, dst_vals=None, bad_val=-999.):
        if dst_vals is None:
            dst_vals = np.zeros(len(self._map)) + bad_val
        rtn = np.choose(src_values.take(self._map) < bad_val,
                        (src_values.take(self._map), dst_vals))
        rtn[self._bad] = bad_val
        dst_vals[:] = rtn

        return rtn

    def test(self, dst_grid, src_grid):
        return all(np.diff(src_grid.get_offset()) > 2)

    def name(self):
        return 'CellToPoint'
