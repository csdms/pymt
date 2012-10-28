#! /usr/bin/env python

import unittest
from unittest import defaultTestLoader as loader

from cmt.grids.tests.test_raster import *
from cmt.grids.tests.test_rectilinear import *
from cmt.nc.tests.test_nc import *

if __name__ == '__main__':
    unittest.main ()

