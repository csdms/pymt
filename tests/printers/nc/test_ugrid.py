import pytest

import numpy as np

from pymt.printers.nc.ugrid import (
    NetcdfRectilinearField,
    NetcdfStructuredField,
    NetcdfUnstructuredField,
)


def new_rectilinear(**kwds):
    from pymt.grids import RectilinearField

    ndims = kwds.pop("ndims", 1)
    shape = np.random.randint(2, 101 + 1, ndims)
    args = []
    for size in shape:
        args.append(np.cumsum((1.0 - np.random.random(size))))

    return RectilinearField(*args, **kwds)


_GRID_TYPE = {
    "rectilinear": NetcdfRectilinearField,
    "structured": NetcdfStructuredField,
    "unstructured": NetcdfUnstructuredField,
}


@pytest.mark.parametrize("ndims", (1, 2, 3))
@pytest.mark.parametrize("grid", ("rectilinear", "structured", "unstructured"))
def test_rectilinear_points(tmpdir, grid, ndims):
    field = new_rectilinear(
        ndims=ndims,
        coordinate_names=("elevation", "latitude", "longitude"),
        units=("m", "degrees_north", "degrees_east"),
    )
    data = np.arange(field.get_point_count())
    field.add_field("air_temperature", data, centering="point", units="F")

    with tmpdir.as_cwd():
        _GRID_TYPE[grid]("rectilinear.nc", field)
        assert os.path.isfile("rectilinear.nc")
