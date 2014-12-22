import os

import yaml
import numpy as np
from numpy.testing import assert_array_almost_equal, assert_almost_equal

from nose.tools import assert_list_equal, assert_raises

from cmt.services.constant.constant import ConstantScalars
from cmt.utils.run_dir import cd_temp


def test_initialize():
    with cd_temp() as _:
        with open('params.yml', 'w') as fp:
            yaml.dump({'foo': 2, 'bar': 3.}, fp)
        c = ConstantScalars()
        c.initialize('params.yml')

    assert_list_equal(c.get_output_var_names(), ['foo', 'bar'])
    assert_list_equal(c.get_input_var_names(), [])

    assert_array_almost_equal(c.get_grid_values('foo'), np.array(2.))
    assert_array_almost_equal(c.get_grid_values('bar'), np.array(3.))
    with assert_raises(KeyError):
        c.get_grid_values('baz')


def test_time_funcs():
    with cd_temp() as _:
        with open('params.yml', 'w') as fp:
            yaml.dump({'foo': 2, 'bar': 3.}, fp)
        c = ConstantScalars()
        c.initialize('params.yml')

    assert_almost_equal(c.get_start_time(), 0.)
    assert_almost_equal(c.get_current_time(), 0.)

    c.update_until(12.5)
    assert_almost_equal(c.get_current_time(), 12.5)


def test_grid_funcs():
    with cd_temp() as _:
        with open('params.yml', 'w') as fp:
            yaml.dump({'foo': 2, 'bar': 3.}, fp)
        c = ConstantScalars()
        c.initialize('params.yml')

    assert_array_almost_equal(c.get_grid_shape('foo'), (1, ))
    assert_array_almost_equal(c.get_grid_spacing('foo'), (1, ))
    assert_array_almost_equal(c.get_grid_origin('foo'), (0, ))

    with assert_raises(KeyError):
        c.get_grid_shape('baz')
    with assert_raises(KeyError):
        c.get_grid_spacing('baz')
    with assert_raises(KeyError):
        c.get_grid_origin('baz')
