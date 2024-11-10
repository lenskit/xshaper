"""
Shaperate record format for serialization.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, TypeAlias
from uuid import UUID

from pydantic import BaseModel, Field, JsonValue

RunMeta: TypeAlias = dict[str, JsonValue]
"Type of run metadata."
RunStatus: TypeAlias = Literal["completed", "failed", "aborted", "unfinished"]
"""
A run's completion status.
"""


class RunRecord(BaseModel):
    """
    Record for a single run.
    """

    run_id: UUID
    "The identifier for this run."
    parent_id: UUID | None = None
    "The identifier for this run's parent."
    anchor_id: UUID | None = None
    """
    The identifier for the nearest anchor in this run's run tree.

    A run can be marked as an *anchor* (with the ``anchor=True`` option) to
    indicate that it should form an intermediate root for the run records. This
    is common for tasks such as cross-validation or parameter sweeps, where a
    single root run covers the overall sweep but it is desirable to easily treat
    each individual segment of the sweep as a separate logical run; marking the
    segments as anchors makes it easy to locate all of their component runs in
    the run log.
    """
    root_id: UUID | None = None
    "The identifier for the root of this run's run tree."
    concurrent: bool = False
    "Whether this run is concurent with its siblings (e.g. worker processes)."

    tags: set[str] = Field(default_factory=set)
    "The run's tags (to enable search or querying later)."

    meta: RunMeta = Field(default_factory=dict)
    "Additional client-specified metadata for this run."

    start_time: datetime
    "The wall-clock time when this run started."
    end_time: datetime | None = None
    "The wall-clock time when this run concluded."
    status: RunStatus | None = None
    """
    The run's completion status, or ``None`` if the run is still in progress.
    ``None`` is only used for run-in-progress records; when run records are
    incorporated into the run log, it is converted to ``unfinished``.
    """

    machine: MachineRecord | None = None
    "The machine on which this run was run (if ``None``, inherits from parent)."


class MachineRecord(BaseModel):
    """
    Information about the machine on which a run is running.  Several of these
    bits come from the Python :mod:`platform` module.  Linux distribution
    information comes from the ``/etc/os-release`` file (see
    :func:`platform.freedesktop_os_release`).
    """

    name: str
    "A friendly or logical name for the machine."
    hostname: str
    "The machine's hostname."
    os: str
    "The operating system name (as reported by :func:`platform.system`)."
    os_version: str
    "The operating system version (as reported by :func:`platform.release`)."
    arch: str
    "The machine architecture (as reported by :func:`platform.machine`)."

    distro_id: str | None = None
    "The Linux distribution ID (e.g. debian, ubuntu)."
    distro_version: str | None = None
    "The Linux distribution version."
