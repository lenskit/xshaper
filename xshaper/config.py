"""
eXperiment Shaperate configuration.
"""

from __future__ import annotations

from os import PathLike
from pathlib import Path

_configured: bool = False
_log_dir: Path | None = None


def configure(log_dir: PathLike[str]):
    """
    Configure the shaperate.
    """
    global _configured, _log_dir
    if _configured:
        raise RuntimeError("shaperate already configured")

    _log_dir = Path(log_dir)
    _configured = True


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
        return ld / "recorded"
