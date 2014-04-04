import unittest
import os

from cmt.utils.which import which


class TestWhich(unittest.TestCase):
    def test_not_in_path(self):
        self.assertIsNone(which('does-not-exist'))

    def test_path_is_dir(self):
        self.assertIsNone(which(os.getcwd()))

    def test_relative_path_is_executable(self):
        self.assertIsInstance(which('python'), str)
        self.assertTrue(os.path.isabs(which('python')))

    def test_abs_path_is_executable(self):
        python = which('python')
        self.assertEqual(python, which(python))
