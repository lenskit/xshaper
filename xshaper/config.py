"""
eXperiment Shaperate configuration.
"""

from __future__ import annotations

from os import PathLike
from pathlib import Path

_log_dir: Path | None = None


def configure(log_dir: PathLike[str] | None = None):
    """
    Configure the shaperate.

    Args:
        log_dir:
            The location of the shaperate log directory, when logs are recorded.
        monitor_frequency:
            The frequency for background system monitoring tasks (in seconds).
    """
    global _log_dir

    if log_dir is not None:
        _log_dir = Path(log_dir)


def log_dir() -> Path | None:
    """
    Get the configured log dir.
    """
    return _log_dir


def lobby_dir() -> Path | None:
    """
    Get the directory for the log record lobby (``log_dir/lobby``).  This is
    where records are written before they are integrated into the permanent log.
    """
    ld = log_dir()
    if ld is not None:
        return ld / "lobby"
