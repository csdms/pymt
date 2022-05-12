from ._version import __version__

from gimli import UnitSystem
from .model_collection import ModelCollection

MODELS = ModelCollection()

__all__ = ["__version__", "UnitSystem", "MODELS"]
