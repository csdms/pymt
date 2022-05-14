#! /bin/env python

import numpy as np
from scipy.spatial import KDTree

from .imapper import IGridMapper, IncompatibleGridError

# from .mapper import IncompatibleGridError


def map_points_to_cells(coords, src_grid, src_point_ids, bad_val=-1):
    (dst_x, dst_y) = coords

    point_to_cell_id = np.empty(len(dst_x), dtype=int)
    point_to_cell_id.fill(bad_val)

    for (j, point_id) in enumerate(src_point_ids):
        for cell_id in src_grid.get_shared_cells(point_id):
            if src_grid.is_in_cell(dst_x[j], dst_y[j], cell_id):
                point_to_cell_id[j] = cell_id

    return point_to_cell_id


class CellToPoint(IGridMapper):

    _name = "CellToPoint"

    def initialize(self, dest_grid, src_grid, **kwds):
        if not CellToPoint.test(dest_grid, src_grid):
            raise IncompatibleGridError(dest_grid.name, src_grid.name)
        dst_x = dest_grid.get_x()
        dst_y = dest_grid.get_y()

        tree = KDTree(list(zip(src_grid.get_x(), src_grid.get_y())))
        (_, self._nearest_src_id) = tree.query(list(zip(dst_x, dst_y)))

        self._map = map_points_to_cells(
            (dst_x, dst_y), src_grid, self._nearest_src_id, bad_val=-1
        )
        self._bad = self._map == -1

    def run(self, src_values, **kwds):
        dst_vals = kwds.get("dst_vals", None)
        bad_val = kwds.get("bad_val", -999.0)

        if dst_vals is None:
            dst_vals = np.zeros(len(self._map)) + bad_val

        rtn = np.choose(
            src_values.take(self._map) < bad_val, (src_values.take(self._map), dst_vals)
        )
        rtn[self._bad] = bad_val
        dst_vals[:] = rtn

        return rtn

    @staticmethod
    def test(dst_grid, src_grid):
        return all(np.diff(src_grid.get_offset()) > 2)

    @property
    def name(self):
        return self._name
