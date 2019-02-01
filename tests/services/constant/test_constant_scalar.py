import numpy as np
import pytest
import yaml
from pytest import approx

from pymt.services.constant.constant import ConstantScalars


def test_initialize(tmpdir):
    with tmpdir.as_cwd():
        with open("params.yml", "w") as fp:
            yaml.dump({"foo": 2, "bar": 3.0}, fp)
        c = ConstantScalars()
        c.initialize("params.yml")

    names = c.get_output_var_names()
    names.sort()
    assert names == ["bar", "foo"]
    assert c.get_input_var_names() == []

    assert c.get_value("foo") == approx(np.array(2.0))
    assert c.get_value("bar") == approx(np.array(3.0))
    with pytest.raises(KeyError):
        c.get_value("baz")


def test_time_funcs(tmpdir):
    with tmpdir.as_cwd():
        with open("params.yml", "w") as fp:
            yaml.dump({"foo": 2, "bar": 3.0}, fp)
        c = ConstantScalars()
        c.initialize("params.yml")

    assert c.get_start_time() == approx(0.0)
    assert c.get_current_time() == approx(0.0)

    c.update_until(12.5)
    assert c.get_current_time() == approx(12.5)


def test_grid_funcs(tmpdir):
    with tmpdir.as_cwd():
        with open("params.yml", "w") as fp:
            yaml.dump({"foo": 2, "bar": 3.0}, fp)
        c = ConstantScalars()
        c.initialize("params.yml")

    assert c.get_var_grid("foo") == 0

    assert c.get_grid_shape(0) == (1,)
    assert c.get_grid_spacing(0) == (1,)
    assert c.get_grid_origin(0) == (0,)

    with pytest.raises(KeyError):
        c.get_var_grid("baz")
