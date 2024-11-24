"""
Record run times.
"""

import os
import time

from ..model import TimeRecord


class TimeRecorder:
    record: TimeRecord
    start_timer: float
    start_ostimes: os.times_result

    def __init__(self, record: TimeRecord):
        self.record = record

    def start(self):
        self.start_timer = time.perf_counter()
        self.start_ostimes = os.times()

    def finish(self):
        pass

    def update(self):
        c_timer = time.perf_counter()
        c_ostimes = os.times()

        self.record.wall = c_timer - self.start_timer
        self.record.self_cpu_usr = c_ostimes.user - self.start_ostimes.user
        self.record.self_cpu_sys = c_ostimes.system - self.start_ostimes.system
