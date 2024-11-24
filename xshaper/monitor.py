"""
Monitoring thread for recording resource usage.
"""

from __future__ import annotations

import logging
from threading import Thread
from time import perf_counter
from typing import Any, TypeAlias

import zmq

from .recorders.compute import measure_compute
from .run import STATE

XSocket: TypeAlias = zmq.Socket[bytes]
XZMQ: TypeAlias = zmq.Context[XSocket]

SIGNAL_ADDR = "inproc://xshaper-monitor-signal"

_log = logging.getLogger(__name__)
_monitor: Monitor | None = None


def active_monitor() -> Monitor | None:
    return _monitor


class Monitor:
    """
    Activate advanced resource monitoring.  When enabled, more sophisticated
    measurements (such as power, CPU utilization, and memory use) are available,
    and in-progress run records are periodically saved to disk.

    The resulting monitor should be used as a context manager, and will shut down
    when the context exits.

    Args:
        update_frequency:
            The frequency (in seconds) for checking resource usage.
        save_frequency:
            The frequency (in seconds) for saving in-progress run records.
    """

    update_frequency: float
    save_frequency: float

    zmq: XZMQ
    _backend: MonitorThread
    _signal: XSocket

    def __init__(self, update_frequency: float = 0.5, save_frequency: float = 5.0):
        global _monitor
        if _monitor is not None:
            raise RuntimeError("only one monitor can be created")

        self.update_frequency = update_frequency
        self.save_frequency = save_frequency
        self.zmq = zmq.Context()

        self._backend = MonitorThread(self)
        self._backend.start()

        self._signal = self.zmq.socket(zmq.REQ)
        self._signal.connect(SIGNAL_ADDR)

        _monitor = self

    def refresh(self):
        """
        Request an immediate refresh, waiting until it is acknowledged.
        """
        self._signal.send(b"update")
        reply = self._signal.recv()
        if reply != b"updated":
            _log.warning("unexpected signal reply %r", reply)

    def shutdown(self):
        global _monitor

        _log.debug("shutting down monitor thread")
        try:
            self._signal.send(b"shutdown")
            _res = self._signal.recv()
            self._signal.close()
            self._backend.join()

            self.zmq.term()
        except Exception as e:
            self.zmq.destroy()
            raise e
        finally:
            _monitor = None

    def __enter__(self) -> Monitor:
        return self

    def __exit__(self, exc_type: type[Exception], exc_value: Exception, _tb: Any):
        self.shutdown()


class MonitorThread(Thread):
    active: bool = True

    def __init__(self, monitor: Monitor):
        super().__init__(name="XShaper-Monitor", daemon=True)
        self.monitor = monitor

    def run(self) -> None:
        with self.monitor.zmq.socket(zmq.REP) as signal:
            signal.bind(SIGNAL_ADDR)

            poller = zmq.Poller()
            poller.register(signal, zmq.POLLIN)
            last_save = perf_counter()
            last_update = last_save

            now = perf_counter()

            while self.active:
                save_wait = self.monitor.save_frequency - (now - last_save)
                upd_wait = self.monitor.update_frequency - (now - last_update)

                timeout = int(min(save_wait, upd_wait) * 1000)
                if timeout > 20:
                    ready = dict(poller.poll(timeout))
                else:
                    ready = {}

                update = False
                save = False
                reply = None

                if signal in ready:
                    reply, update = self._handle_signal(signal)

                now = perf_counter()
                if not update:
                    # do we want an update within the next 20 ms?
                    if now - last_update - self.monitor.update_frequency > -0.02:
                        update = True
                if not save:
                    if now - last_save - self.monitor.save_frequency > -0.02:
                        save = True

                if update:
                    self._update_active()
                if save:
                    self._save_active()

                if reply is not None:
                    signal.send(reply)

    def _handle_signal(self, signal: zmq.Socket[bytes]) -> tuple[bytes | None, bool]:
        msg = signal.recv(zmq.NOBLOCK)

        if msg == b"shutdown":
            _log.debug("received shutdown signal, terminating thread")
            self.active = False
            return b"goodbye", False

        elif msg == b"update":
            return b"updated", True

        else:
            _log.warning("invalid message: %s", msg.decode())
            return None, False

    def _update_active(self):
        compute = measure_compute()

        with STATE.lock:
            for run in STATE.active_runs:
                run.time_recorder.update()
                run.compute_recorder.update(compute)

    def _save_active(self):
        with STATE.lock:
            for run in STATE.active_runs:
                run.save()
