"""
eXperiment Shaperate - monitor and record experiment runs.
"""

from .config import configure
from .monitor import Monitor
from .run import Run

__all__ = ["configure", "Run", "Monitor"]

try:
    from ._version import version

    __version__ = version
except ImportError:
    __version__ = "UNKNOWN"
