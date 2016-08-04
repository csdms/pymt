import unittest

from cmt.grids.grid_type import (GridType, GridTypeRectilinear,
                                 GridTypeStructured, GridTypeUnstructured)


class TestGridType(unittest.TestCase):
    def test_rectilinear(self):
        type = GridTypeRectilinear()
        self.assertEqual(str(type), 'rectilinear')
        self.assertEqual(type, 'rectilinear')
        self.assertEqual(type, GridTypeRectilinear())
        self.assertNotEqual(type, GridTypeStructured)
        self.assertNotEqual(type, GridType)
        self.assertIsInstance(type, GridType)

    def test_structured(self):
        type = GridTypeStructured()
        self.assertEqual(str(type), 'structured')
        self.assertEqual(type, 'structured')
        self.assertEqual(type, GridTypeStructured())
        self.assertNotEqual(type, GridTypeRectilinear)
        self.assertNotEqual(type, GridType)
        self.assertIsInstance(type, GridType)

    def test_unstructured(self):
        type = GridTypeUnstructured()
        self.assertEqual(str(type), 'unstructured')
        self.assertEqual(type, 'unstructured')
        self.assertEqual(type, GridTypeUnstructured())
        self.assertNotEqual(type, GridTypeRectilinear)
        self.assertNotEqual(type, GridType)
        self.assertIsInstance(type, GridType)
