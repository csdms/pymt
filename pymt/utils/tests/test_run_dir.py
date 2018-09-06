import os
import shutil

import pytest

from pymt.utils.run_dir import open_run_dir


def test_run_dir():
    init_dir = os.getcwd()
    with open_run_dir("/"):
        assert os.getcwd() == "/"
    assert os.getcwd() == init_dir


def test_relative_dir():
    init_dir = os.getcwd()
    with open_run_dir(".."):
        assert os.getcwd() == os.path.abspath(os.path.join(init_dir, ".."))
    assert os.getcwd() == init_dir


def test_nested_dirs():
    init_dir = os.getcwd()
    with open_run_dir("/"):
        assert os.getcwd() == "/"
        with open_run_dir("/bin"):
            assert os.getcwd() == "/bin"
        assert os.getcwd() == "/"
    assert os.getcwd() == init_dir


def test_nested_relative_dirs():
    init_dir = os.getcwd()
    with open_run_dir("/usr/bin"):
        assert os.getcwd() == "/usr/bin"
        with open_run_dir(".."):
            assert os.getcwd() == "/usr"
        assert os.getcwd() == "/usr/bin"
    assert os.getcwd() == init_dir


def test_dir_does_not_exist():
    with pytest.raises(OSError):
        with open_run_dir("/not/a/real/dir"):
            pass


def test_negative_dir():
    init_dir = os.getcwd()
    with open_run_dir("/"):
        assert os.getcwd() == "/"
        with open_run_dir(".."):
            assert os.getcwd() == "/"
        assert os.getcwd() == "/"
    assert os.getcwd() == init_dir


def test_do_not_gobble_exception():
    init_dir = os.getcwd()
    try:
        with open_run_dir("/usr"):
            assert os.getcwd() == "/usr"
            raise ValueError()
    except ValueError:
        assert os.getcwd() == init_dir
    else:
        raise AssertionError("statement should not be reached")


def test_missing_dir():
    init_dir = os.getcwd()
    with pytest.raises(OSError):
        with open_run_dir("./not/a/dir"):
            pass
    assert not os.path.isdir(os.path.join(init_dir, "not/a/dir"))


def test_create_missing_dir():
    init_dir = os.getcwd()
    with open_run_dir("./not/a/dir", create=True):
        assert os.getcwd() == os.path.join(init_dir, "not/a/dir")
    assert os.getcwd() == init_dir
    assert os.path.isdir(os.path.join(init_dir, "not/a/dir"))
    shutil.rmtree("./not")
