#! /bin/env python

import numpy as np
from imapper import IGridMapper
from cmt.mappers import IncompatibleGridError

#try:
#    from esmp import *
#except ImportError:
#    import warnings
#    warnings.warn ('Unable to import ESMP for cmt.mappers.esmp',
#                   RuntimeWarning)
#from esmp import *
import ESMP


class EsmpMapper(IGridMapper):
    def initialize(self, dest_grid, src_grid,
                   method=ESMP.ESMP_REGRIDMETHOD_CONSERVE,
                   unmapped=ESMP.ESMP_UNMAPPEDACTION_ERROR):
        if not self.test(dest_grid, src_grid):
            raise IncompatibleGridError(dest_grid.name,
                                        src_grid.name)

        self._src = EsmpUnstructuredField(src_grid.get_x(), src_grid.get_y(),
                                          src_grid.get_connectivity(),
                                          src_grid.get_offset())
        self._dst = EsmpUnstructuredField(dest_grid.get_x(), dest_grid.get_y(),
                                          dest_grid.get_connectivity(),
                                          dest_grid.get_offset())

        self.init_fields()

        self._routehandle = ESMP.ESMP_FieldRegridStore(self.get_source_field(),
                                                       self.get_dest_field(),
                                                       method, unmapped)

    def run(self, src_values, dest_values=None):
        src_ptr = self.get_source_data()
        src_ptr.data = src_values

        dst_ptr = ESMP.ESMP_FieldGetPtr(dst_field)
        dst_ptr = self.get_dest_data()

        if dest_values is not None:
            dst_ptr.data = dest_values
        else:
            dst_ptr.fill(0.)

        ESMP.ESMP_FieldRegrid(self.get_source_field(), self.get_dest_field(),
                              self._routehandle)

        return dest_values

    def finalize(self):
        ESMP.ESMP_FieldRegridRelease(self._routehandle)

    def get_source_field(self):
        return self._src.as_esmp('src')

    def get_dest_field(self):
        return self._dst.as_esmp('dst')

    def get_source_data(self):
        return ESMP.ESMP_FieldGetPtr(self.get_source_field())

    def get_dest_data(self):
        return ESMP.ESMP_FieldGetPtr(self.get_dest_field())


class EsmpCellToCell(EsmpMapper):
    def init_fields(self):
        data = np.empty(self._src.get_cell_count(), dtype=np.float64)
        self._src.add_field('src', data, centering='zonal')

        data = np.empty(self._dst.get_cell_count(), dtype=np.float64)
        self._dst.add_field('dst', data, centering='zonal')

    def test(self, dst_grid, src_grid):
        return (all(np.diff(dst_grid.get_offset()) > 2) and
                all(np.diff(src_grid.get_offset()) > 2))

    def name(self):
        return 'CellToCell'


class EsmpPointToPoint(EsmpMapper):
    def init_fields(self):
        data = np.empty(self._src.get_point_count(), dtype=np.float64)
        self._src.add_field('src', data, centering='point')

        data = np.empty(self._dst.get_point_count(), dtype=np.float64)
        self._dst.add_field('dst', data, centering='point')

    def test(self, dst_grid, src_grid):
        return True

    def name(self):
        return 'PointToPoint'
