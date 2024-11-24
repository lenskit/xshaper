"""
Shaperate data model and record format(s) for serialization.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, TypeAlias
from uuid import UUID

from pydantic import BaseModel, Field, JsonValue

__all__ = [
    "RunRecord",
    "RunMeta",
    "RunStatus",
    "MachineRecord",
    "TimeRecord",
    "MemoryRecord",
    "PowerRecord",
]

RunMeta: TypeAlias = dict[str, JsonValue]
"""
Type of run metadata.
"""
RunStatus: TypeAlias = Literal["completed", "failed", "aborted", "unfinished"]
"""
A run's completion status.
"""


class RunRecord(BaseModel):
    """
    Record for a single run.
    """

    run_id: UUID
    "The unique identifier for this run."
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

    start_time: datetime = Field(default_factory=datetime.now)
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

    time: TimeRecord = Field(default_factory=lambda: TimeRecord())
    "Wall and CPU time consumption."
    cpu: CPURecord | None = None
    "Approximate CPU consumption."
    memory: MemoryRecord | None = None
    "Estimated memory use."
    power: PowerRecord | None = None
    "Estimated power consumption."


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


class TimeRecord(BaseModel):
    """
    Record of the time (both wall-clock and CPU) consumed by a run.  All times
    are in seconds.
    """

    wall: float = 0
    """
    Wall-clock elapsed time.

    .. note::

        This may *not* be the same as the difference between the run record's
        start and end times, because it uses the system's monontonic clock (when
        possible) whereas system time may have changed.
    """
    self_cpu: float | None = None
    "Total CPU time (this run)."
    self_cpu_usr: float | None = None
    "Userspace CPU time (this run)."
    self_cpu_sys: float | None = None
    "System CPU time (this run)."

    tot_cpu: float | None = None
    "Total CPU time (including concurrent children)."
    tot_cpu_usr: float | None = None
    "Userspace CPU time (including concurrent children)."
    tot_cpu_sys: float | None = None
    "System CPU time (including concurrent children)."


class CPURecord(BaseModel):
    """
    Record of CPU utilization statistics.
    """

    physical_cores: int | None = None
    "Total phsyical cores on the system."

    logical_cores: int | None = None
    "Total logcial cores on the system."

    python_cpus: int | None = None
    """
    Total CPUs reported by Python.  This is the result of :func:`os.cpu_count`;
    it will usually equal :attr:`total_cpus` unless the ``PYTHON_CPU_COUNT``
    variable is set.
    """

    process_cpus: int | None = None
    """
    The number of CPUs available to this process, as reported by
    :func:`os.process_cpu_count` or :func:`os.sched_getaffinity`.
    """

    avg_process_util: float | None = None
    """
    Average CPU utilization by this process during the run. Not normalized by
    process count (100% = full use of 1 CPU).

    .. seealso:: :meth:`psutil.Process.cpu_percent`
    """

    avg_system_util: float | None = None
    """
    Average system-wide CPU utilization while this process is running.

    .. seealso:: :func:`psutil.cpu_percent`
    """


class MemoryRecord(BaseModel):
    """
    Record of the memory used by the run (approximate).
    """

    peak_rss: float | None = None
    """
    Peak memory (resident set on Unix, working set on Windows) as measured by
    monitoring the process memory statistics.
    """
    peak_shared: float | None = None
    """
    Peak sharable memory (Linux ``shared``) as measured by monitoring the
    process memory statistics.
    """

    max_rss: float | None = None
    """
    Maximum resident memory as measured by the operating system.  For multiple
    runs in a single process, will not be accurate (will be the maximum RSS of
    this run and any previous run in the same process).  Does not account for
    child processes.
    """


class PowerRecord(BaseModel):
    """
    Record of the (estimated) power consumed by a run.  All values are in
    watt-hours.
    """

    cpu_power: float | None = None
    """
    Power consumed by the CPU.  When reported, this is based on the system's CPU
    on-package power measurement.
    """
    ram_power: float | None = None
    """
    Power consumed by RAM.  When reported, this is based on the system chipset
    or SoC package's on-package RAM power measurement.
    """
    gpu_power: float | None = None
    """
    Power consumed by the GPU(s).  When reported, this is based on the GPU
    chipset's power consumption reporting (e.g. via NVML for NVidia cards).
    """
    chassis_power: float | None = None
    """
    Power consumed by the entire machine.  This is typically measured by the
    chassis PSU, datacenter PDU, or by a metering smart plug (see e.g. EMERS_).

    .. _EMERS: https://github.com/ISG-Siegen/emers
    """
