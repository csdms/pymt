import os

from nose.tools import (assert_is_none, assert_is_instance, assert_true,
                        assert_equal)

from cmt.utils.which import which


def test_not_in_path():
    assert_is_none(which('does-not-exist'))


def test_path_is_dir():
    assert_is_none(which(os.getcwd()))


def test_relative_path_is_executable():
    assert_is_instance(which('python'), str)
    assert_true(os.path.isabs(which('python')))


def test_abs_path_is_executable():
    python = which('python')
    assert_equal(python, which(python))
