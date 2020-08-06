__all__ = []

import sys

from .utils import err, out


def _load_models():
    from collections import OrderedDict, namedtuple
    import pkg_resources

    from .framework.bmi_bridge import bmi_factory

    models = OrderedDict()

    failed = []
    for entry_point in pkg_resources.iter_entry_points(group="pymt.plugins"):
        try:
            model = entry_point.load()
        except Exception:
            failed.append(entry_point.name)
        else:
            model = bmi_factory(model)
            models[entry_point.name] = model

    if len(models) > 0:
        out("models: {0}".format(", ".join(models.keys())))
    else:
        out("models: (none)")
    if failed:
        err("failed to load the following models: {0}".format(", ".join(failed)))

    Models = namedtuple("Models", models.keys())
    return Models(*models.values())


models_loaded = False

if not models_loaded:
    for model in _load_models():
        __all__.append(model.__name__)
        setattr(sys.modules[__name__], model.__name__, model)
    models_loaded = True

try:
    del model
except NameError:
    pass
del sys, _load_models
