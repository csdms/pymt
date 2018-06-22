#! /usr/bin/env python

import unittest
import numpy as np

from pymt.grids import UniformRectilinear, Rectilinear, Structured, Unstructured
from pymt.grids import (
    is_uniform_rectilinear,
    is_rectilinear,
    is_structured,
    is_unstructured,
)


class TestUniformRectilinearAssertions(unittest.TestCase):
    def test_is_uniform_rectilinear(self):
        grid = UniformRectilinear((5, 4), (1, 1), (0, 0))
        self.assertTrue(is_uniform_rectilinear(grid))

    def test_is_not_uniform_rectilinear(self):
        grid = Rectilinear([1., 2., 4., 8.], [1., 2., 3.])
        self.assertFalse(is_uniform_rectilinear(grid))


class TestRectilinearAssertions(unittest.TestCase):
    def test_is_rectilinear(self):
        grid = Rectilinear([1., 2., 4., 8.], [1., 2., 3.])
        self.assertTrue(is_rectilinear(grid))

    def test_is_not_rectilinear(self):
        grid = Structured([0, 1, 2, 0, 1, 2], [0, 0, 0, 1, 1, 1], (3, 2))
        self.assertFalse(is_rectilinear(grid))

    def test_is_strictly_rectilinear(self):
        grid = UniformRectilinear((5, 4), (1, 1), (0, 0))
        self.assertFalse(is_rectilinear(grid))

    def test_is_not_strictly_rectilinear(self):
        grid = UniformRectilinear((5, 4), (1, 1), (0, 0))
        self.assertTrue(is_rectilinear(grid, strict=False))


class TestStructuredAssertions(unittest.TestCase):
    def test_is_structured(self):
        grid = Structured([0, 1, 2, 0, 1, 2], [0, 0, 0, 1, 1, 1], (3, 2))
        self.assertTrue(is_structured(grid))

    def test_is_not_structured(self):
        grid = Unstructured(
            [0, 1, 2, 0, 1, 2], [0, 0, 0, 1, 1, 1], [0, 1, 4, 3, 1, 2, 5, 4], [4, 8]
        )
        self.assertFalse(is_structured(grid))

    def test_is_strictly_structured(self):
        grid = UniformRectilinear((5, 4), (1, 1), (0, 0))
        self.assertFalse(is_structured(grid))

    def test_is_not_strictly_structured(self):
        grid = UniformRectilinear((5, 4), (1, 1), (0, 0))
        self.assertTrue(is_structured(grid, strict=False))


class TestUnstructuredAssertions(unittest.TestCase):
    def test_is_unstructured(self):
        grid = Unstructured(
            [0, 1, 2, 0, 1, 2], [0, 0, 0, 1, 1, 1], [0, 1, 4, 3, 1, 2, 5, 4], [4, 8]
        )
        self.assertTrue(is_unstructured(grid))

    def test_is_strictly_unstructured(self):
        grid = UniformRectilinear((5, 4), (1, 1), (0, 0))
        self.assertFalse(is_unstructured(grid))

    def test_is_not_strictly_unstructured(self):
        grid = UniformRectilinear((5, 4), (1, 1), (0, 0))
        self.assertTrue(is_unstructured(grid, strict=False))


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestUniformRectilinearAssertions
    )
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRectilinearAssertions)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStructuredAssertions)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUnstructuredAssertions)
    return suite


if __name__ == "__main__":
    unittest.main()
