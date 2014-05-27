import os
import shutil
from nose.tools import assert_equal, assert_raises, assert_true, assert_false

from cmt.utils.run_dir import open_run_dir


def test_run_dir():
    init_dir = os.getcwd()
    with open_run_dir('/'):
        assert_equal(os.getcwd(), '/')
    assert_equal(os.getcwd(), init_dir)


def test_relative_dir():
    init_dir = os.getcwd()
    with open_run_dir('..'):
        assert_equal(os.getcwd(), os.path.abspath(os.path.join(init_dir, '..')))
    assert_equal(os.getcwd(), init_dir)


def test_nested_dirs():
    init_dir = os.getcwd()
    with open_run_dir('/'):
        assert_equal(os.getcwd(), '/')
        with open_run_dir('/bin'):
            assert_equal(os.getcwd(), '/bin')
        assert_equal(os.getcwd(), '/')
    assert_equal(os.getcwd(), init_dir)


def test_nested_relative_dirs():
    init_dir = os.getcwd()
    with open_run_dir('/usr/bin'):
        assert_equal(os.getcwd(), '/usr/bin')
        with open_run_dir('..'):
            assert_equal(os.getcwd(), '/usr')
        assert_equal(os.getcwd(), '/usr/bin')
    assert_equal(os.getcwd(), init_dir)


def test_dir_does_not_exist():
    with assert_raises(OSError):
        with open_run_dir('/not/a/real/dir'):
            pass


def test_negative_dir():
    init_dir = os.getcwd()
    with open_run_dir('/'):
        assert_equal(os.getcwd(), '/')
        with open_run_dir('..'):
            assert_equal(os.getcwd(), '/')
        assert_equal(os.getcwd(), '/')
    assert_equal(os.getcwd(), init_dir)


def test_do_not_gobble_exception():
    init_dir = os.getcwd()
    try:
        with open_run_dir('/usr'):
            assert_equal(os.getcwd(), '/usr')
            raise ValueError()
    except ValueError:
        assert_equal(os.getcwd(), init_dir)
    else:
        raise AssertionError('statement should not be reached')


def test_missing_dir():
    init_dir = os.getcwd()
    with assert_raises(OSError):
        with open_run_dir('./not/a/dir'):
            pass
    assert_false(os.path.isdir(os.path.join(init_dir, 'not/a/dir')))


def test_create_missing_dir():
    init_dir = os.getcwd()
    with open_run_dir('./not/a/dir', create=True):
        assert_equal(os.getcwd(), os.path.join(init_dir, 'not/a/dir'))
    assert_equal(os.getcwd(), init_dir)
    assert_true(os.path.isdir(os.path.join(init_dir, 'not/a/dir')))
    shutil.rmtree('./not')
