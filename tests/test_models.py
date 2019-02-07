#! /usr/bin/env python
import os

import pytest

from pymt import models


@pytest.mark.parametrize("cls", models.__all__)
def test_model_setup(cls):
    model = models.__dict__[cls]()
    args = model.setup()
    assert os.path.isfile(os.path.join(args[1], args[0]))


@pytest.mark.parametrize("cls", models.__all__)
def test_model_initialize(cls):
    model = models.__dict__[cls]()
    args = model.setup()
    model.initialize(*args)

    assert model.initdir == args[1]
    assert model._initialized


@pytest.mark.parametrize("cls", models.__all__)
def test_model_irf(cls):
    model = models.__dict__[cls]()
    model.initialize(*model.setup())
    model.update()
    assert model.get_current_time() > model.get_start_time()
    model.finalize()
