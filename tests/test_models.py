#! /usr/bin/env python
import os

import pytest

from pymt import models

MODELS = [models.__dict__[name] for name in models.__all__]
MODELS.sort(key=lambda item: item.__name__)


@pytest.mark.parametrize("cls", MODELS)
def test_model_setup(cls):
    model = cls()
    args = model.setup()
    assert os.path.isfile(os.path.join(args[1], args[0]))


@pytest.mark.parametrize("cls", MODELS)
def test_model_initialize(cls):
    model = cls()
    args = model.setup()
    model.initialize(*args)

    assert model.initdir == args[1]
    assert model._initialized


@pytest.mark.parametrize("cls", MODELS)
def test_model_update(cls):
    model = cls()
    model.initialize(*model.setup())
    model.update()
    # assert model.time > model.start_time


@pytest.mark.parametrize("cls", MODELS)
def test_model_finalize(cls):
    model = cls()
    model.initialize(*model.setup())
    model.update()
    model.finalize()
    assert not model._initialized
