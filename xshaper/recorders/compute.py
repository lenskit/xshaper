"""
Record local compute resources (CPU and memory).
"""

import os
from dataclasses import dataclass
from time import perf_counter

from psutil import Process, cpu_count, cpu_percent

from ..model import CPURecord, MemoryRecord, RunRecord


@dataclass(frozen=True, slots=True)
class ComputeMeasurements:
    time: float
    sys_pct: float
    proc_pct: float

    rss: int
    shared: int | None


class ComputeRecorder:
    record: RunRecord

    # memory of highest memory usage
    _peak_rss: float = 0
    _peak_shared: float = 0

    # accumulators to average CPU utilization percentage
    _last_time: float
    _tot_time: float = 0.0
    _tot_proc_pct: float = 0.0
    _tot_sys_pct: float = 0.0

    def __init__(self, record: RunRecord):
        self.record = record

        self._tot_time = 0.0
        self._tot_proc_pct = 0.0
        self._tot_sys_pct = 0.0

    def start(self):
        physical_cores = cpu_count(False)
        logical_cores = cpu_count(True)
        python_cpus = os.cpu_count()

        if hasattr(os, "process_cpu_count"):
            process_cpus = os.process_cpu_count()  # type: ignore
        elif hasattr(os, "sched_getaffinity"):
            process_cpus = len(os.sched_getaffinity())  # type: ignore
        else:
            process_cpus = None

        if self.record.cpu is None:
            self.record.cpu = CPURecord(
                physical_cores=physical_cores,
                logical_cores=logical_cores,
                python_cpus=python_cpus,
                process_cpus=process_cpus,  # type: ignore
            )
        if self.record.memory is None:
            self.record.memory = MemoryRecord()

    def finish(self):
        try:
            import resource

            m = resource.getrusage(resource.RUSAGE_SELF)
            if self.record.memory is not None:
                self.record.memory.max_rss = m.ru_maxrss
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

        if self.record.cpu is not None:
            self.record.cpu.avg_process_util = self._tot_proc_pct / self._tot_time
            self.record.cpu.avg_system_util = self._tot_sys_pct / self._tot_time

        if self.record.memory is not None:
            if metrics.rss > self._peak_rss:
                self._peak_rss = metrics.rss
                self.record.memory.peak_rss = metrics.rss

            if metrics.shared is not None and metrics.shared > self._peak_shared:
                self._peak_shared = metrics.shared
                self.record.memory.peak_shared = metrics.shared


def measure_compute() -> ComputeMeasurements:
    now = perf_counter()
    sys_cpu = cpu_percent()
    p = Process()
    with p.oneshot():
        proc_cpu = p.cpu_percent()
        mem = p.memory_info()

    return ComputeMeasurements(now, sys_cpu, proc_cpu, mem.rss, getattr(mem, "shared", None))
