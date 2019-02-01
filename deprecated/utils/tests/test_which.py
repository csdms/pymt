import os

from pymt.utils.which import which


def test_not_in_path():
    assert which("does-not-exist") is None


def test_path_is_dir():
    assert which(os.getcwd()) is None


def test_relative_path_is_executable():
    assert isinstance(which("python"), str)
    assert os.path.isabs(which("python"))


def test_abs_path_is_executable():
    python = which("python")
    assert python == which(python)
