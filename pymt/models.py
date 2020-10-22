__all__ = []

import sys

from .model_collection import ModelCollection

for name, cls in ModelCollection().items():
    __all__.append(name)
    setattr(sys.modules[__name__], name, cls)

try:
    del name, cls
except NameError:
    pass
del sys, ModelCollection
