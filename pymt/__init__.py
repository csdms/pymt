import numpy as np
from gimli.units import UnitSystem

from ._version import __version__
from .model_collection import ModelCollection

np.set_printoptions(legacy="1.21")

MODELS = ModelCollection()

__all__ = ["__version__", "UnitSystem", "MODELS"]
