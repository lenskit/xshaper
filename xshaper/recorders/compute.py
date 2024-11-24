"""
Record local compute resources (CPU and memory).
"""

import os
from dataclasses import dataclass
from time import perf_counter

from psutil import Process, cpu_count, cpu_percent

from ..model import CPURecord, MemoryRecord


@dataclass(frozen=True, slots=True)
class ComputeMeasurements:
    time: float
    sys_pct: float
    proc_pct: float

    rss: int
    shared: int | None


class ComputeRecorder:
    cpu: CPURecord
    memory: MemoryRecord

    # memory of highest memory usage
    _peak_rss: float = 0
    _peak_shared: float = 0

    # accumulators to average CPU utilization percentage
    _last_time: float
    _tot_time: float = 0.0
    _tot_proc_pct: float = 0.0
    _tot_sys_pct: float = 0.0

    def __init__(self, cpu: CPURecord, memory: MemoryRecord):
        self.cpu = cpu
        self.memory = memory

        self._tot_time = 0.0
        self._tot_proc_pct = 0.0
        self._tot_sys_pct = 0.0

    def start(self):
        self.cpu.physical_cores = cpu_count(False)
        self.cpu.logical_cores = cpu_count(True)
        self.cpu.python_cpus = os.cpu_count()

        if hasattr(os, "process_cpu_count"):
            self.cpu.process_cpus = os.process_cpu_count()  # type: ignore
        elif hasattr(os, "sched_getaffinity"):
            self.cpu.process_cpus = len(os.sched_getaffinity())  # type: ignore

    def finish(self):
        try:
            import resource

            m = resource.getrusage(resource.RUSAGE_SELF)
            self.memory.max_rss = m.ru_maxrss
        except ImportError:
            return

    def update(self, metrics: ComputeMeasurements):
        if not hasattr(self, "_last_time"):
            self._last_time = metrics.time
            return

        diff = metrics.time - self._last_time

        self._last_time = diff
        self._tot_time += diff
        self._tot_proc_pct += diff * metrics.proc_pct
        self._tot_sys_pct += diff * metrics.sys_pct

        self.cpu.avg_process_util = self._tot_proc_pct / self._tot_time
        self.cpu.avg_system_util = self._tot_sys_pct / self._tot_time

        if metrics.rss > self._peak_rss:
            self._peak_rss = metrics.rss
            self.memory.peak_rss = metrics.rss

        if metrics.shared is not None and metrics.shared > self._peak_shared:
            self._peak_shared = metrics.shared
            self.memory.peak_shared = metrics.shared


def measure_compute() -> ComputeMeasurements:
    now = perf_counter()
    sys_cpu = cpu_percent()
    p = Process()
    with p.oneshot():
        proc_cpu = p.cpu_percent()
        mem = p.memory_info()

    return ComputeMeasurements(now, sys_cpu, proc_cpu, mem.rss, getattr(mem, "shared", None))
