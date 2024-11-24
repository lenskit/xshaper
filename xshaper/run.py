"""
Classes and functions for recording runs.
"""

from __future__ import annotations

import logging
from datetime import datetime
from threading import RLock
from typing import Any, Iterable, Self
from uuid import UUID, uuid4

from .config import lobby_dir
from .model import RunMeta, RunRecord, RunStatus

_log = logging.getLogger(__name__)


class RunState:
    "Current and parent runs."

    _stack: list[Run]
    _anchors: list[Run]
    lock: RLock

    def __init__(self) -> None:
        self._stack = []
        self._anchors = []
        self.lock = RLock()

    @property
    def root(self) -> Run | None:
        with self.lock:
            if self._stack:
                return self._stack[0]
            else:
                return None

    @property
    def current(self) -> Run | None:
        with self.lock:
            if self._stack:
                return self._stack[-1]
            else:
                return None

    @property
    def anchor(self) -> Run | None:
        with self.lock:
            if self._anchors:
                return self._anchors[-1]
            else:
                return None

    def push_run(self, run: Run, anchor: bool = False):
        with self.lock:
            self._stack.append(run)
            if anchor or (not self._anchors and not run.parent_id):
                self._anchors.append(run)

    def pop_run(self, run: Run):
        with self.lock:
            if self._stack[-1] is not run:
                raise RuntimeError("cannot pop non-current run")
            del self._stack[-1]
            if self._anchors and self._anchors[-1] is run:
                del self._anchors[-1]


class Run:
    """
    A current or completed run, recording its state and preparing the records.

    Runs should usually be used as context managers, e.g.::

        with xshaper.run(...):
            pass

    For advanced usage scenarios, there are also manual :meth:`begin` and
    :meth:`end` methods.

    Args:
        tags:
            The tags for this run.
        meta:
            Additional metadata for this run (JSON-compatible dictionary).  This
            dictionary is *copied* into the run record.
        concurrent:
            ``True`` to record this run as concurrent.
        parent:
            A parent run ID; should only be used when creating worker process
            runs.
        anchor:
            If ``True``, mark this run as an anchor run.
    """

    id: UUID
    record: RunRecord
    is_anchor: bool = False

    _start_time: float

    def __init__(
        self,
        tags: Iterable[str] = (),
        meta: RunMeta = {},
        concurrent: bool = False,
        parent: UUID | None = None,
        anchor: bool = False,
    ):
        self.id = uuid4()
        self.is_anchor = anchor
        if parent is None and (current := STATE.current):
            parent = current.id

        self.record = RunRecord(
            run_id=self.id,
            parent_id=parent,
            tags=set(tags),
            meta=dict(meta),
            concurrent=concurrent,
        )
        if rrun := STATE.root:
            self.record.root_id = rrun.id
        if arun := STATE.anchor:
            self.record.anchor_id = arun.id

    @property
    def parent_id(self) -> UUID | None:
        "Get the run's parent ID."
        return self.record.parent_id

    def begin(self):
        """
        Begin the run.  You should usually use the run as a context manager
        instead of calling this method directly.
        """
        _log.debug("beginning run %s", self.id)

        self.record.start_time = datetime.now()

        STATE.push_run(self, self.is_anchor)

    def end(self, status: RunStatus = "completed"):
        """
        Finish the run.  You should usually use the run as a context manager
        instead of calling this method directly.
        """
        _log.debug("ending run %s (state=%s)", self.id, status)
        STATE.pop_run(self)

        self.record.status = status
        self.record.end_time = datetime.now()

        self.save()

    def save(self):
        lobby = lobby_dir()
        if lobby is None:
            return

        runfile = lobby / f"{self.id}.json"
        _log.debug("saving run state to %s", runfile)

        # write to temp file first, so we don't leave corrupted JSON lying around
        tmpfile = runfile.with_suffix(".json.tmp")
        tmpfile.write_text(self.record.model_dump_json(exclude_unset=True))
        tmpfile.rename(runfile)

    def __enter__(self) -> Self:
        self.begin()
        return self

    def __exit__(self, exc_type: type[Exception] | None, exc_value: Exception | None, _tb: Any):
        if isinstance(exc_value, KeyboardInterrupt):
            self.end("aborted")
        elif exc_type is not None:
            self.end("failed")
        else:
            self.end()


STATE: RunState = RunState()