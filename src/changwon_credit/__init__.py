"""Changwon corporate credit analysis package."""

from importlib import metadata

try:
    __version__ = metadata.version("changwon-corp-credit")
except metadata.PackageNotFoundError:  # pragma: no cover - fallback for editable installs
    __version__ = "0.0.0"

__all__ = ["__version__"]
