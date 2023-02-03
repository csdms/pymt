from gimli import UnitSystem

from ._version import __version__
from .model_collection import ModelCollection

MODELS = ModelCollection()

__all__ = ["__version__", "UnitSystem", "MODELS"]
