#! /usr/bin/env python

import unittest
from cmt.grids.map import RectilinearMap as Rectilinear
from cmt.mappers import find_mapper
import numpy as np

class TestMapper (unittest.TestCase):

    def test_point_to_point (self):
        src = Rectilinear ([0, 1, 2], [0, 2])
        dst = Rectilinear ([.5, 1.5, 2.5], [.25, 1.25])

        src_vals = np.arange (src.get_point_count ())

        from cmt.mappers import NearestVal

        mapper = NearestVal ()
        mapper.initialize (dst, src)
        dst_vals = mapper.run (src_vals)

        self.assertListEqual (list (dst_vals), list ([0., 1., 2., 3., 4., 5.]))

        mappers = find_mapper (dst, src)
        self.assertEqual (len (mappers), 3)
        self.assertEqual (mappers[0].name (), 'PointToPoint')

        src_vals[2] = -999
        dst_vals = np.zeros (dst.get_point_count ())-1
        dummy = mapper.run (src_vals, dst_vals)

        self.assertListEqual (list (dst_vals), list ([0., 1., -1., 3., 4., 5.]))

    def test_cell_to_point (self):
        # The source grid looks like,
        #
        #    (0) ------ (1)
        #     |          |
        #     |          |
        #    (2) ------ (3)
        #     |          |
        #     |          |
        #    (4) ------ (5)
        #     |          |
        #     |          |
        #    (7) ------ (7)
        #

        from cmt.mappers import CellToPoint
        from cmt.grids.map import (UniformRectilinearMap as
                                   UniformRectilinear)
        from cmt.grids.map import (UnstructuredPointsMap as
                                   UnstructuredPoints)

        (dst_x, dst_y) = (np.array ([.45, 1.25, 3.5]),
                          np.array ([.75, 2.25, 3.25]))

        src = UniformRectilinear ((2,4), (2, 1), (0, 0))
        dst = UnstructuredPoints (dst_x, dst_y)

        src_vals = np.arange (src.get_cell_count (), dtype=np.float)

        mapper = CellToPoint ()
        mapper.initialize (dst, src)
        dst_vals = mapper.run (src_vals, bad_val=-999)

        self.assertListEqual (list (dst_vals), [0., 2., -999.])

        src_vals = np.arange (src.get_cell_count (), dtype=np.float)
        src_vals[0] = -9999
        dst_vals = np.zeros (dst.get_point_count ()) + 100
        dummy = mapper.run (src_vals, dst_vals)

        self.assertListEqual (list (dst_vals), [100., 2., -999.])

    def test_point_to_cell (self):
        from cmt.mappers import PointToCell
        from cmt.grids.map import (UniformRectilinearMap as
                                   UniformRectilinear)
        from cmt.grids.map import (UnstructuredPointsMap as
                                   UnstructuredPoints)

        (src_x, src_y) = (np.array ([.45, 1.25, 3.5, .0, 1.]),
                          np.array ([.75, 2.25, 3.25, .9, 1.1]))

        src = UnstructuredPoints (src_x, src_y)
        dst = UniformRectilinear ((2,4), (2, 1), (0, 0))

        src_vals = np.arange (src.get_point_count (), dtype=np.float)

        mapper = PointToCell ()
        mapper.initialize (dst, src)

        dst_vals = mapper.run (src_vals, bad_val=-999)
        self.assertListEqual (list (dst_vals), [1.5, 4., 1.])

        dst_vals = mapper.run (src_vals, bad_val=-999, method=np.sum)
        self.assertListEqual (list (dst_vals), [3., 4., 1.])

        src_vals[0] = -9999
        dst_vals = np.zeros (dst.get_cell_count ()) - 1
        dummy = mapper.run (src_vals, dst_vals)
        self.assertListEqual (list (dst_vals), [-1., 4., 1.])

    def test_point_to_cell_on_edges (self):
        from cmt.mappers import PointToCell
        from cmt.grids.map import (UniformRectilinearMap as
                                   UniformRectilinear)
        from cmt.grids.map import (UnstructuredPointsMap as
                                   UnstructuredPoints)

        (src_x, src_y) = (np.array ([0, .5, 1., 2, 3.5]),
                          np.array ([1., 1., .0, 3, 3.]))
        src = UnstructuredPoints (src_x, src_y)
        dst = UniformRectilinear ((2,4), (2, 1), (0, 0))

        mapper = PointToCell ()
        mapper.initialize (dst, src)

        src_vals = np.arange (src.get_point_count (), dtype=np.float)
        dst_vals = np.zeros (dst.get_cell_count ())-1
        dummy = mapper.run (src_vals, dst_vals)
        self.assertListEqual (list (dst_vals), [1., 0.5, 3.])

    def test_point_to_cell_big (self):
        from cmt.mappers import PointToCell
        from cmt.grids.map import (UniformRectilinearMap as
                                   UniformRectilinear)
        from cmt.grids.map import (UnstructuredPointsMap as
                                   UnstructuredPoints)
        (m, n) = (20, 40)
        (src_x, src_y) = np.meshgrid (range (m), range (n))
        src = UnstructuredPoints (src_y, src_x)
        dst = UniformRectilinear ((n+1,m+1), (1, 1), (-.5, -.5))

        mapper = PointToCell ()
        mapper.initialize (dst, src)

        src_vals = np.arange (src.get_point_count (), dtype=np.float)
        dst_vals = np.zeros (dst.get_cell_count (), dtype=np.float)-1
        dummy = mapper.run (src_vals, dst_vals)
        self.assertListEqual (list (dst_vals), list (src_vals))

def suite ():
    suite = unittest.TestLoader ().loadTestsFromTestCase (TestMapper)
    return suite

if __name__ == '__main__':
    unittest.main ()

