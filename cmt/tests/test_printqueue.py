#! /usr/bin/env python

import os
import unittest
import numpy as np

from cmt.printqueue import CmiTimedPrintQueue, FieldCollection
from cmt.grids import RasterField
from cmt import namespace as ns

class TestCmiTimedPrintQueue (unittest.TestCase):
    generated_files = [
        'Test_Elevation_0000.vtu',
        'Test_Elevation_0001.vtu',
        'Test_Temperature_0000.vtu',
        'Test_Temperature_0001.vtu',
        'AddFilesTest_Elevation_0000.vtu',
        'AddFilesTest_Thickness_0000.vtu',
        'Test1_Elevation.nc',
        'Test1_Temperature.nc',
    ]

    def setUp (self):
        for file in self.generated_files:
            try:
                os.remove (file)
            except OSError:
                pass

    def tearDown (self):
        for file in self.generated_files:
            try:
                os.remove (file)
            except OSError:
                pass

    def test_timed_print_queue_push (self):
        port = self.create_test_port ()

        globs = {'Dir': '/tmp', 'SimulationName': '', 'FileFormat': 'NC'}
        locals = {'Dir': '.', 'SimulationName': 'Test', 'FileFormat': 'VTK',
                  'Var/Elevation': 'on', 'Var/Temperature': 'on', 'Var/Depth': 'off'}
        pq = CmiTimedPrintQueue (port, globs)

        pq.push (locals)
        pq.print_all (1.)

        self.assertTrue (os.path.isfile ('./Test_Elevation_0000.vtu'))
        self.assertTrue (os.path.isfile ('./Test_Temperature_0000.vtu'))
        self.assertTrue (not os.path.isfile ('./Test_Depth_0000.vtu'))

        # When appending data to a VTK database, a new file is created with
        # the suffix incremented by one.
        self.assertTrue (not os.path.isfile ('./Test_Elevation_0001.vtu'))
    
        pq.print_all (2.)
        self.assertTrue (os.path.isfile ('./Test_Elevation_0001.vtu'))

    def test_timed_print_queue_add_files (self):
        port = self.create_test_port ()

        globs = {'Dir': '/tmp', 'SimulationName': '', 'FileFormat': 'NC'}
        locals = {'Point/Dir': '.', 'Point/SimulationName': 'AddFilesTest', 'Point/FileFormat': 'VTK',
                  'Point/Var/Elevation': 'on', 'Point/Var/Thickness': 'on',
                  'Zonal/Dir': '.', 'Zonal/SimulationName': 'AddFilesTest', 'Zonal/FileFormat': 'VTK',
                  'Zonal/Var/Temperature': 'on'}
        globs.update (locals)
        pq = CmiTimedPrintQueue (port, globs)

        pq.add_files ('Point/')
        pq.print_all (1.)

        self.assertTrue (os.path.isfile ('./AddFilesTest_Elevation_0000.vtu'))
        self.assertTrue (os.path.isfile ('./AddFilesTest_Thickness_0000.vtu'))
        self.assertTrue (not os.path.isfile ('./AddFilesTest_Temperature_0000.vtu'))

    def test_timed_print_queue_nc (self):
        port = self.create_test_port ()

        attrs = {'/Model/SimulationName': '', '/Model/FileFormat': 'nc',
                 '/Model/Output/Grid/Dir': '.', '/Model/Output/Grid/Interval': 1.,
                 '/Model/Output/Grid/SimulationName': 'Test1', '/Model/Output/Grid/FileFormat': 'nc',
                 '/Model/Output/Grid/Var/Elevation': 'on', '/Model/Output/Grid/Var/Temperature': 'on',
                 '/Model/Output/Grid/Var/Depth': 'off'}

        globs = ns.extract_base (attrs, '/Model/')
        pq = CmiTimedPrintQueue (port, globs)
        pq.add_files ('Output/Grid/')
        pq.print_all (1.)

        self.assertTrue (os.path.isfile ('./Test1_Elevation.nc'))
        self.assertTrue (os.path.isfile ('./Test1_Temperature.nc'))
        self.assertTrue (not os.path.isfile ('./Test1_Depth.nc'))

        # When appending data to a NetCDF file, the data are appended
        # to the existing file and so there is no counter in the file name.

        self.assertTrue (not os.path.isfile ('./Test1_Elevation_0000.nc'))
    
        pq.print_all (2.)
        self.assertTrue (not os.path.isfile ('./Test1_Elevation_0001.nc'))

    def test_next_print_time (self):
        import sys

        port = self.create_test_port ()

        globs = {'Dir': '/tmp', 'SimulationName': '', 'FileFormat': 'NC',
                 'Interval': 2.}

        pq = CmiTimedPrintQueue (port, globs)

        time = pq.next_print_time ()
        #self.assertIsNone (time)
        self.assertAlmostEqual (time, sys.float_info.max)

        #locals = {'Dir': '.', 'SimulationName': 'Test', 'FileFormat': 'VTK',
        locals = {
                  'Interval': 4,
                  'Var/Elevation': 'on', 'Var/Temperature': 'on', 'Var/Depth': 'off'}
        pq.push (locals)

        time = pq.next_print_time ()
        self.assertEqual (time, 4.)

    def create_test_port (self):
        f = RasterField ((3,2), (1,1), (0,0))
        f.add_field ('Elevation', [1., 2., 3, 4, 5, 6], centering='point')
        f.add_field ('Thickness', [10., 20.], centering='zonal')

        g = RasterField ((3,3), (1,1), (0,0))
        g.add_field ('Temperature', -1*np.arange (9.), centering='point')

        # Create a print queue for variable Elevation and Thickness on
        # the first grid, and Temperature on the second grid.

        port = FieldCollection (dict (Elevation=f, Temperature=g, Thickness=f))

        return port

if __name__ == '__main__':
    unittest.main ()

