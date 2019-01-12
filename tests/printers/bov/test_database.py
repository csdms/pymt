import os

import numpy as np

from pymt.grids import RasterField
from pymt.printers.bov.database import Database


def test_bov_database(tmpdir):
    data = np.arange(6.)
    field = RasterField((3, 2), (1., 1.), (0., 0.))
    field.add_field("Elevation", data, centering="point")

    with tmpdir.as_cwd():
        db = Database()
        db.open("Bov_database.bov", "Elevation")

        # Write the field to the database. Since BOV files only
        # store one variable, append the variable name to the file name.

        db.write(field)
        assert os.path.isfile("Bov_database_0000.bov")

        data *= 2.
        db.write(field)
        assert os.path.isfile("Bov_database_0001.bov")

        data *= 2.
        db.write(field)
        assert os.path.isfile("Bov_database_0002.bov")

        db.close()
