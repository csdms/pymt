import pkg_resources
import traceback
from collections import UserDict

from .framework.bmi_bridge import bmi_factory


class ModelLoadError(Exception):

    def __init__(self, name, reason=None):
        self._name = name
        self._reason = reason or "no reason given"

    def __str__(self):
        return f"unable to load model ({self._name}):\n{self._reason}"


def _load_entry_point(entry_point):
    try:
        model = entry_point.load()
    except Exception as error:
        raise ModelLoadError(
            entry_point.name,
            reason=traceback.format_exc(),
            # reason=str(error),
        )
    else:
        Model = bmi_factory(model)
        Model.__name__ = entry_point.name
        Model.__qualname__ = entry_point.name
        Model.__module__ = __name__

    return entry_point.name, Model


# class ModelCollection(UserDict):
class ModelCollection:
    def __new__(cls):
        models = []
        errors = []
        for entry_point in pkg_resources.iter_entry_points(group="pymt.plugins"):
            try:
                models.append(ModelCollection.load_entry_point(entry_point))
            except ModelLoadError as error:
                errors.append((entry_point.name, str(error)))
        for name, model in models:
            setattr(cls, name, property(lambda self, name=name: self._data[name]))

        inst = super().__new__(cls)
        inst._errors = tuple(errors)
        inst._data = dict(models)

        return inst

    def __getitem__(self, name):
        return self._data[name]

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def values(self):
        return self._data.values()

    def __iter__(self):
        return self._data.__iter__()

    def __len__(self):
        return len(self._data)

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return repr(set(self.keys()))

    @property
    def errors(self):
        return self._errors

    @staticmethod
    def load_entry_point(entry_point):
        try:
            model = entry_point.load()
        except Exception as error:
            raise ModelLoadError(entry_point.name, reason=traceback.format_exc())
        else:
            Model = bmi_factory(model)
            Model.__name__ = entry_point.name
            Model.__qualname__ = entry_point.name
            Model.__module__ = "pymt.models"

        return entry_point.name, Model
