"""
eXperiment Shaperate - monitor and record experiment runs.
"""

from .config import configure
from .monitor import Monitor
from .run import Run, current_run

__all__ = ["configure", "Run", "current_run", "Monitor"]

try:
    from ._version import version

    __version__ = version
except ImportError:
    __version__ = "UNKNOWN"
