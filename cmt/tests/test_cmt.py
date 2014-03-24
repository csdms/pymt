#! /usr/bin/env python

import unittest
#from unittest import defaultTestLoader as loader

from cmt.grids.tests.test_raster import *
from cmt.grids.tests.test_rectilinear import *
from cmt.grids.tests.test_field import *
from cmt.grids.tests.test_esmp import *
from cmt.nc.tests.test_nc import *
from cmt.nc.tests.test_database import *
from cmt.vtk.tests.test_vtk import *
from cmt.mappers.tests.test_mapper import *

if __name__ == '__main__':
    unittest.main ()

