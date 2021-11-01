import os

from pymt.printers.nc.read import field_fromfile

_BASE_URL_FOR_TEST_FILES = (
    "https://csdms.colorado.edu/data" "/benchmark/ugrid/"
)
_TMP_DIR = "tmp"


def setup():
    import tempfile

    globals().update({"_TMP_DIR": tempfile.mkdtemp(dir=".")})


def teardown():
    from shutil import rmtree

    rmtree(_TMP_DIR)


def fetch_data_file(filename):
    from six.moves import urllib

    remote_file = urllib.request.urlopen(_BASE_URL_FOR_TEST_FILES + filename)
    local_file = os.path.join(_TMP_DIR, filename)
    with open(local_file, "wb") as netcdf_file:
        netcdf_file.write(remote_file.read())

    return local_file


def test_unstructured_2d():
    field_fromfile(fetch_data_file("unstructured.2d.nc"), fmt="NETCDF4")


def test_rectilinear_1d():
    field_fromfile(fetch_data_file("rectilinear.1d.nc"), fmt="NETCDF4")


def test_rectilinear_2d():
    field_fromfile(fetch_data_file("rectilinear.2d.nc"), fmt="NETCDF4")


def test_rectilinear_3d():
    field_fromfile(fetch_data_file("rectilinear.3d.nc"), fmt="NETCDF4")
