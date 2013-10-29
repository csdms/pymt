#! /usr/bin/env python

import os
import unittest
import numpy as np

from cmt.printqueue.port_printer import (VtkPortPrinter, NcPortPrinter,
                                         BovPortPrinter)

from printqueue_test_utils import (TestPortPrinterBase,
                                   UniformRectilinearGridPort)


class TestVtkPortPrinter(TestPortPrinterBase):
    def test_one_file(self):
        expected_files = ['landscape_surface__elevation_0000.vtu']

        port = UniformRectilinearGridPort()
        printer = VtkPortPrinter(port, 'landscape_surface__elevation')
        printer.open()
        printer.write()

        self._assert_and_remove(expected_files)

    def test_time_series(self):
        expected_files = [
            'sea_floor_surface_sediment__mean_of_grain_size_0000.vtu',
            'sea_floor_surface_sediment__mean_of_grain_size_0001.vtu',
            'sea_floor_surface_sediment__mean_of_grain_size_0002.vtu',
            'sea_floor_surface_sediment__mean_of_grain_size_0003.vtu',
            'sea_floor_surface_sediment__mean_of_grain_size_0004.vtu',
        ]

        port = UniformRectilinearGridPort()
        printer = VtkPortPrinter(
            port, 'sea_floor_surface_sediment__mean_of_grain_size')
        printer.open()
        for _ in xrange(5):
            printer.write()
        printer.close()

        self._assert_and_remove(expected_files)

    def test_multiple_files(self):
        expected_files = [
            'sea_surface__temperature_0000.vtu',
        ]

        port = UniformRectilinearGridPort()
        for _ in xrange(5):
            printer = VtkPortPrinter(port, 'sea_surface__temperature')
            printer.open()
            printer.write()
            printer.close()

        self._assert_and_remove(expected_files)


class TestNcPortPrinter(TestPortPrinterBase):
    def test_default(self):
        expected_files = ['landscape_surface__elevation.nc']

        port = UniformRectilinearGridPort()
        printer = NcPortPrinter(port, 'landscape_surface__elevation')
        printer.open()
        printer.write()

        self._assert_and_remove(expected_files)

    def test_multiple_files(self):
        expected_files = [
            'sea_surface__temperature.nc',
            'sea_surface__temperature.0.nc',
            'sea_surface__temperature.1.nc',
            'sea_surface__temperature.2.nc',
            'sea_surface__temperature.3.nc',
        ]

        port = UniformRectilinearGridPort()
        for _ in xrange(5):
            printer = NcPortPrinter(port, 'sea_surface__temperature')
            printer.open()
            printer.write()

        self._assert_and_remove(expected_files)

    def test_time_series(self):
        expected_files = ['sea_floor_surface_sediment__mean_of_grain_size.nc']

        port = UniformRectilinearGridPort()
        printer = NcPortPrinter(
            port, 'sea_floor_surface_sediment__mean_of_grain_size')
        printer.open()
        for _ in xrange(5):
            printer.write()
        printer.close()

        self._assert_and_remove(expected_files)


class TestBovPortPrinter(TestPortPrinterBase):
    def test_default(self):
        expected_files = [
            'landscape_surface__elevation_0000.dat',
            'landscape_surface__elevation_0000.bov',
        ]

        port = UniformRectilinearGridPort()
        printer = BovPortPrinter(port, 'landscape_surface__elevation')
        printer.open()
        printer.write()

        self._assert_and_remove(expected_files)

    def test_multiple_files(self):
        expected_files = [
            'sea_surface__temperature_0000.dat',
            'sea_surface__temperature_0000.bov',
        ]
        port = UniformRectilinearGridPort()
        for _ in xrange(5):
            printer = BovPortPrinter(port, 'sea_surface__temperature')
            printer.open()
            printer.write()

        self._assert_and_remove(expected_files)

    def test_time_series(self):
        expected_files = [
            'sea_floor_surface_sediment__mean_of_grain_size_0000.dat',
            'sea_floor_surface_sediment__mean_of_grain_size_0000.bov',
            'sea_floor_surface_sediment__mean_of_grain_size_0001.dat',
            'sea_floor_surface_sediment__mean_of_grain_size_0001.bov',
            'sea_floor_surface_sediment__mean_of_grain_size_0002.dat',
            'sea_floor_surface_sediment__mean_of_grain_size_0002.bov',
            'sea_floor_surface_sediment__mean_of_grain_size_0003.dat',
            'sea_floor_surface_sediment__mean_of_grain_size_0003.bov',
            'sea_floor_surface_sediment__mean_of_grain_size_0004.dat',
            'sea_floor_surface_sediment__mean_of_grain_size_0004.bov',
        ]

        port = UniformRectilinearGridPort()
        printer = BovPortPrinter(
            port, 'sea_floor_surface_sediment__mean_of_grain_size')
        printer.open()
        for _ in xrange(5):
            printer.write()
        printer.close()

        self._assert_and_remove(expected_files)
