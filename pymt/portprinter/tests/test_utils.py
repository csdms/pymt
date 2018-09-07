#! /usr/bin/env python


import unittest

import numpy as np

import pymt.portprinter.utils as pp


class TestFixArrayShape(unittest.TestCase):
    def test_no_unknown_dimension(self):
        shape = pp.fix_unknown_shape((4, 5), 20)
        self.assertTupleEqual((4, 5), shape)

        shape = pp.fix_unknown_shape((), 0)
        self.assertTupleEqual((0,), shape)

    def test_one_unknown_dimension(self):
        shape = pp.fix_unknown_shape((4, -1), 20)
        self.assertTupleEqual((4, 5), shape)

        shape = pp.fix_unknown_shape((-1, 5), 20)
        self.assertTupleEqual((4, 5), shape)

        shape = pp.fix_unknown_shape((-1,), 20)
        self.assertTupleEqual((20,), shape)

    def test_multiple_unknown_dimension(self):
        with self.assertRaises(pp.DimensionError):
            pp.fix_unknown_shape((-1, -1), 20)

    def test_shape_mismatch(self):
        with self.assertRaises(pp.DimensionError):
            pp.fix_unknown_shape((20, -1), 21)

        with self.assertRaises(pp.DimensionError):
            pp.fix_unknown_shape((), 20)

    def test_0d(self):
        shape = pp.fix_unknown_shape((-1, 4, 0), 20)
        self.assertTupleEqual((5, 4, 0), shape)


class TestFindUnknownDimension(unittest.TestCase):
    def test_no_unknown_dimension(self):
        dimen = pp.find_unknown_dimension((4, 5))
        self.assertEqual(None, dimen)

        dimen = pp.find_unknown_dimension((4,))
        self.assertEqual(None, dimen)

        dimen = pp.find_unknown_dimension(())
        self.assertEqual(None, dimen)

    def test_one_unknown_dimension(self):
        dimen = pp.find_unknown_dimension((-1, 5))
        self.assertEqual(0, dimen)
        dimen = pp.find_unknown_dimension((4, -1))
        self.assertEqual(1, dimen)
        dimen = pp.find_unknown_dimension((-1,))
        self.assertEqual(0, dimen)

    def test_multiple_unknown_dimensions(self):
        with self.assertRaises(pp.DimensionError):
            pp.find_unknown_dimension((-1, -1))
        with self.assertRaises(pp.DimensionError):
            pp.find_unknown_dimension((-1, 4, -1))

    def test_shape_as_int_array(self):
        dimen = pp.find_unknown_dimension(np.array((4, -1, 5), dtype=np.int64))
        self.assertEqual(1, dimen)

    def test_shape_as_list(self):
        dimen = pp.find_unknown_dimension([4, 5, -1])
        self.assertEqual(2, dimen)

    def test_shape_as_tuple(self):
        dimen = pp.find_unknown_dimension((4, 5, 10, -1))
        self.assertEqual(3, dimen)

    def test_0d(self):
        dimen = pp.find_unknown_dimension((0, -1))
        self.assertEqual(1, dimen)
