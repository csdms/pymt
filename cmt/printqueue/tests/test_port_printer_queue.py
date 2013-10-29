#! /usr/bin/env python

import cmt.printqueue.port_printer_queue as ppq

from printqueue_test_utils import (TestPortPrinterBase,
                                   UniformRectilinearGridPort)

class TestPortPrinterQueue(TestPortPrinterBase):
    def test_default(self):
        expected_files = [
            'air__density_0000.vtu',
            'air__density_0001.vtu',
            'air__density_0002.vtu',
            'air__density_0003.vtu',
            'air__density_0004.vtu',
            'glacier_top_surface__slope.nc',
        ]

        port = UniformRectilinearGridPort()
        queue = ppq.PortPrinterQueue(port)
        queue.append('air__density', format='vtk')
        queue.append('glacier_top_surface__slope', format='nc')
        queue.open()
        for _ in xrange(5):
            queue.write()
        queue.close()

        self._assert_and_remove(expected_files)
