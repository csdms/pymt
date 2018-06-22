#! /bin/env python

from collections import defaultdict

import numpy as np
from scipy.spatial import KDTree
from six.moves import zip

from .imapper import IGridMapper, IncompatibleGridError

# from .mapper import IncompatibleGridError


def map_cells_to_points(coords, dst_grid, dst_point_ids, bad_val=-1):
    src_x, src_y = coords

    cell_to_point_id = defaultdict(list)
    for (j, point_id) in enumerate(dst_point_ids):
        for cell_id in dst_grid.get_shared_cells(point_id):
            if dst_grid.is_in_cell(src_x[j], src_y[j], cell_id):
                cell_to_point_id[cell_id].append(j)

    return cell_to_point_id


class PointToCell(IGridMapper):
    def initialize(self, dst_grid, src_grid):
        if not self.test(dst_grid, src_grid):
            raise IncompatibleGridError(dst_grid.name, src_grid.name)
        src_x = src_grid.get_x()
        src_y = src_grid.get_y()

        tree = KDTree(list(zip(dst_grid.get_x(), dst_grid.get_y())))
        (_, nearest_dest_id) = tree.query(list(zip(src_x, src_y)))

        self._map = map_cells_to_points(
            (src_x, src_y), dst_grid, nearest_dest_id, bad_val=-1
        )

        self._dst_cell_count = dst_grid.get_cell_count()
        self._src_point_count = src_grid.get_point_count()

    def run(self, src_values, dst_vals=None, bad_val=-999, method=np.mean):
        assert src_values.size == self._src_point_count

        if dst_vals is None:
            dst_vals = np.array([bad_val] * self._dst_cell_count, dtype=np.float)
        assert dst_vals.size == self._dst_cell_count

        for (cell_id, point_ids) in self._map.items():
            if all(src_values[point_ids] > bad_val):
                dst_vals[cell_id] = method(src_values[point_ids])

        return dst_vals

    def test(self, dst_grid, src_grid):
        return all(np.diff(dst_grid.get_offset()) > 2) and src_grid is not None

    def name(self):
        return "PointToCell"
