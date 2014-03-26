#! /usr/bin/env python

import cmt.printqueue.port_printer_queue as ppq

from printqueue_test_utils import (UniformRectilinearGridPort,
                                   assert_isfile_and_remove)


def test_uniform_rectilinear_vtk():
    port = UniformRectilinearGridPort()

    queue = ppq.PortPrinterQueue(port)
    queue.append('air__density', format='vtk')
    queue.open()
    for _ in xrange(5):
        queue.write()
    queue.close()

    assert_isfile_and_remove('air__density_0000.vtu')
    assert_isfile_and_remove('air__density_0001.vtu')
    assert_isfile_and_remove('air__density_0002.vtu')
    assert_isfile_and_remove('air__density_0003.vtu')
    assert_isfile_and_remove('air__density_0004.vtu')


def test_uniform_rectilinear_nc():
    port = UniformRectilinearGridPort()

    queue = ppq.PortPrinterQueue(port)
    queue.append('glacier_top_surface__slope', format='nc')
    queue.open()
    for _ in xrange(5):
        queue.write()
    queue.close()

    assert_isfile_and_remove('glacier_top_surface__slope.nc')

