import numpy as np

from ..grids.esmp import EsmpUnstructuredField
from .imapper import IGridMapper
from .mapper import IncompatibleGridError

try:
    import ESMF as esmf
except ImportError:
    esmf = None
    REGRID_METHOD = None
    UNMAPPED_ACTION = None
else:
    REGRID_METHOD = esmf.RegridMethod.CONSERVE
    UNMAPPED_ACTION = esmf.UnmappedAction.ERROR


class EsmpMapper(IGridMapper):
    _name = None

    @property
    def name(self):
        return self._name

    @staticmethod
    def test(dst_grid, src_grid):
        raise NotImplementedError("test")

    def init_fields(self):
        raise NotImplementedError("init_fields")

    def initialize(self, dest_grid, src_grid, **kwds):
        method = kwds.get("method", REGRID_METHOD)
        unmapped = kwds.get("unmapped", UNMAPPED_ACTION)

        if not EsmpMapper.test(dest_grid, src_grid):
            raise IncompatibleGridError(dest_grid.name, src_grid.name)

        self._src = EsmpUnstructuredField(
            src_grid.get_x(),
            src_grid.get_y(),
            src_grid.get_connectivity(),
            src_grid.get_offset(),
        )
        self._dst = EsmpUnstructuredField(
            dest_grid.get_x(),
            dest_grid.get_y(),
            dest_grid.get_connectivity(),
            dest_grid.get_offset(),
        )

        self.init_fields()
        self._regridder = esmf.Regrid(
            self.get_source_field(),
            self.get_dest_field(),
            regrid_method=method,
            unmapped_action=unmapped,
        )

    def run(self, src_values, **kwds):
        dest_values = kwds.get("dest_values", None)
        src_ptr = self.get_source_data()
        src_ptr[:] = src_values
        # src_ptr.data = src_values

        # dst_ptr = ESMP.ESMP_FieldGetPtr(dst_field)
        dst_ptr = self.get_dest_data()

        if dest_values is not None:
            dst_ptr[:] = dest_values
            # dst_ptr.data = dest_values
        else:
            dst_ptr.fill(0.0)

        # ESMP.ESMP_FieldRegrid(self.get_source_field(), self.get_dest_field(),
        #                      self._routehandle)
        self._regridder(self.get_source_field(), self.get_dest_field())

        return dest_values

    def finalize(self):
        pass
        # ESMP.ESMP_FieldRegridRelease(self._routehandle)

    def get_source_field(self):
        return self._src.as_esmp("src")

    def get_dest_field(self):
        return self._dst.as_esmp("dst")

    def get_source_data(self):
        return self._src.as_esmp("src").data
        # return ESMP.ESMP_FieldGetPtr(self.get_source_field())

    def get_dest_data(self):
        return self._dst.as_esmp("dst").data
        # return ESMP.ESMP_FieldGetPtr(self.get_dest_field())


class EsmpCellToCell(EsmpMapper):
    _name = "CellToCell"

    def init_fields(self):
        data = np.empty(self._src.get_cell_count(), dtype=np.float64)
        self._src.add_field("src", data, centering="zonal")

        data = np.empty(self._dst.get_cell_count(), dtype=np.float64)
        self._dst.add_field("dst", data, centering="zonal")

    @staticmethod
    def test(dst_grid, src_grid):
        return all(np.diff(dst_grid.get_offset()) > 2) and all(
            np.diff(src_grid.get_offset()) > 2
        )


class EsmpPointToPoint(EsmpMapper):
    _name = "PointToPoint"

    def init_fields(self):
        data = np.empty(self._src.get_point_count(), dtype=np.float64)
        self._src.add_field("src", data, centering="point")

        data = np.empty(self._dst.get_point_count(), dtype=np.float64)
        self._dst.add_field("dst", data, centering="point")

    @staticmethod
    def test(dst_grid, src_grid):
        return dst_grid is not None and src_grid is not None
