import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class TaskRecord:
    """Everything the Tasks window needs to render one task's item widget."""
    task_id: str
    name: str
    params: str = ""
    queued_at: Optional[float] = None
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    succeeded: Optional[bool] = None


class TaskQueue:
    def __init__(
        self,
        on_task_start: Callable[[str], None],
        on_task_complete: Callable[[str], None],
        on_task_error: Callable[[str, Exception], None],
    ):
        self._queue: queue.Queue = queue.Queue()
        self._pending: list[TaskRecord] = []
        self._current: Optional[TaskRecord] = None
        self._cancelled: set[str] = set()
        self._completed: list[TaskRecord] = []
        self._lock = threading.Lock()
        self.on_task_start = on_task_start
        self.on_task_complete = on_task_complete
        self.on_task_error = on_task_error
        threading.Thread(target=self._worker, daemon=True).start()

    def submit(self, action: Callable, name: str, params: str = "") -> None:
        task_id = str(uuid.uuid4())
        record = TaskRecord(task_id, name, params, queued_at=time.time())
        with self._lock:
            self._pending.append(record)
        self._queue.put((task_id, action, record))

    def cancel(self, task_id: str) -> None:
        with self._lock:
            self._cancelled.add(task_id)
            self._pending = [r for r in self._pending if r.task_id != task_id]

    def cancel_all(self) -> None:
        """Cancel every task currently pending in the queue (not the one already running)."""
        with self._lock:
            self._cancelled.update(r.task_id for r in self._pending)
            self._pending = []

    def get_pending(self) -> list[TaskRecord]:
        with self._lock:
            return list(self._pending)

    def get_current(self) -> Optional[TaskRecord]:
        with self._lock:
            return self._current

    def get_completed(self) -> list[TaskRecord]:
        """Return finished task records, oldest first."""
        with self._lock:
            return list(self._completed)

    def clear_completed(self) -> None:
        with self._lock:
            self._completed = []

    def _worker(self) -> None:
        while True:
            task_id, action, record = self._queue.get()
            with self._lock:
                if task_id in self._cancelled:
                    self._cancelled.discard(task_id)
                    self._queue.task_done()
                    continue
                self._pending = [r for r in self._pending if r.task_id != task_id]
                record.started_at = time.time()
                self._current = record
            self.on_task_start(record.name)
            try:
                action()
                self.on_task_complete(record.name)
                succeeded = True
            except Exception as e:
                self.on_task_error(record.name, e)
                succeeded = False
            finally:
                with self._lock:
                    self._current = None
                    record.finished_at = time.time()
                    record.succeeded = succeeded
                    self._completed.append(record)
                self._queue.task_done()


class AsyncTaskTracker:
    """Track tasks that are running concurrently, outside of any queue."""

    def __init__(self):
        self._running: dict[str, TaskRecord] = {}
        self._completed: list[TaskRecord] = []
        self._lock = threading.Lock()

    def start(self, name: str, params: str = "") -> str:
        task_id = str(uuid.uuid4())
        record = TaskRecord(task_id, name, params, started_at=time.time())
        with self._lock:
            self._running[task_id] = record
        return task_id

    def finish(self, task_id: str, succeeded: bool = True) -> None:
        with self._lock:
            record = self._running.pop(task_id, None)
            if record is not None:
                record.finished_at = time.time()
                record.succeeded = succeeded
                self._completed.append(record)

    def get_running(self) -> list[TaskRecord]:
        with self._lock:
            return list(self._running.values())

    def get_completed(self) -> list[TaskRecord]:
        """Return finished task records, oldest first."""
        with self._lock:
            return list(self._completed)

    def clear_completed(self) -> None:
        with self._lock:
            self._completed = []
