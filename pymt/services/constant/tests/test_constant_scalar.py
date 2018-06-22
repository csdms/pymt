import os

import yaml
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_almost_equal

from nose.tools import assert_equal, assert_list_equal, assert_raises

from pymt.services.constant.constant import ConstantScalars
from pymt.utils.run_dir import cd_temp


def test_initialize():
    with cd_temp() as _:
        with open("params.yml", "w") as fp:
            yaml.dump({"foo": 2, "bar": 3.}, fp)
        c = ConstantScalars()
        c.initialize("params.yml")

    names = c.get_output_var_names()
    names.sort()
    assert_list_equal(names, ["bar", "foo"])
    assert_list_equal(c.get_input_var_names(), [])

    assert_array_almost_equal(c.get_value("foo"), np.array(2.))
    assert_array_almost_equal(c.get_value("bar"), np.array(3.))
    with assert_raises(KeyError):
        c.get_value("baz")


def test_time_funcs():
    with cd_temp() as _:
        with open("params.yml", "w") as fp:
            yaml.dump({"foo": 2, "bar": 3.}, fp)
        c = ConstantScalars()
        c.initialize("params.yml")

    assert_almost_equal(c.get_start_time(), 0.)
    assert_almost_equal(c.get_current_time(), 0.)

    c.update_until(12.5)
    assert_almost_equal(c.get_current_time(), 12.5)


def test_grid_funcs():
    with cd_temp() as _:
        with open("params.yml", "w") as fp:
            yaml.dump({"foo": 2, "bar": 3.}, fp)
        c = ConstantScalars()
        c.initialize("params.yml")

    assert_equal(c.get_var_grid("foo"), 0)

    assert_array_almost_equal(c.get_grid_shape(0), (1,))
    assert_array_almost_equal(c.get_grid_spacing(0), (1,))
    assert_array_almost_equal(c.get_grid_origin(0), (0,))

    with assert_raises(KeyError):
        c.get_var_grid("baz")
