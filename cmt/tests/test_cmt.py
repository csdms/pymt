#! /usr/bin/env python

import unittest
from unittest import defaultTestLoader as loader

import cmt.grids.tests.test_raster
import cmt.grids.tests.test_rectilinear
import cmt.nc.tests.test_nc

suite = unittest.TestSuite ()
suite.addTests (
    loader.loadTestsFromModule (cmt.grids.tests.test_raster))
suite.addTests (
    loader.loadTestsFromModule (cmt.grids.tests.test_rectilinear))
suite.addTests (
    loader.loadTestsFromModule (cmt.nc.tests.test_nc))

unittest.TextTestRunner (verbosity=2).run (suite)

if __name__ == '__main__':
    #unittest.main ()

    unittest.TextTestRunner (verbosity=2).run (suite)

