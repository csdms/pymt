import pytest

from pymt.printers.nc.read import field_fromfile


@pytest.mark.parametrize(
    "filename",
    [
        "unstructured.2d.nc",
        "rectilinear.1d.nc",
        "rectilinear.2d.nc",
        "rectilinear.3d.nc",
    ],
)
def test_read_netcdf(datadir, filename):
    field_fromfile(datadir / filename, fmt="NETCDF4")
