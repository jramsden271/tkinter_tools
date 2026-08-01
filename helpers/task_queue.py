import queue
import threading
import time
import uuid
from typing import Callable, Optional


class TaskQueue:
    def __init__(
        self,
        on_task_start: Callable[[str], None],
        on_task_complete: Callable[[str], None],
        on_task_error: Callable[[str, Exception], None],
    ):
        self._queue: queue.Queue = queue.Queue()
        self._pending: list[tuple[str, str]] = []
        self._current: Optional[tuple[str, str, float]] = None
        self._cancelled: set[str] = set()
        self._completed: list[tuple[str, str, bool, float]] = []
        self._lock = threading.Lock()
        self.on_task_start = on_task_start
        self.on_task_complete = on_task_complete
        self.on_task_error = on_task_error
        threading.Thread(target=self._worker, daemon=True).start()

    def submit(self, action: Callable, name: str) -> None:
        task_id = str(uuid.uuid4())
        with self._lock:
            self._pending.append((task_id, name))
        self._queue.put((task_id, action, name))

    def cancel(self, task_id: str) -> None:
        with self._lock:
            self._cancelled.add(task_id)
            self._pending = [(tid, n) for tid, n in self._pending if tid != task_id]

    def cancel_all(self) -> None:
        """Cancel every task currently pending in the queue (not the one already running)."""
        with self._lock:
            self._cancelled.update(tid for tid, _ in self._pending)
            self._pending = []

    def get_pending(self) -> list[tuple[str, str]]:
        with self._lock:
            return list(self._pending)

    def get_current(self) -> Optional[tuple[str, str, float]]:
        """Return (task_id, name, start_time) for the task currently executing, if any."""
        with self._lock:
            return self._current

    def get_completed(self) -> list[tuple[str, str, bool, float]]:
        """Return (task_id, name, succeeded, finish_time) for each finished task, oldest first."""
        with self._lock:
            return list(self._completed)

    def clear_completed(self) -> None:
        with self._lock:
            self._completed = []

    def _worker(self) -> None:
        while True:
            task_id, action, name = self._queue.get()
            with self._lock:
                if task_id in self._cancelled:
                    self._cancelled.discard(task_id)
                    self._queue.task_done()
                    continue
                self._pending = [(tid, n) for tid, n in self._pending if tid != task_id]
                self._current = (task_id, name, time.monotonic())
            self.on_task_start(name)
            try:
                action()
                self.on_task_complete(name)
                succeeded = True
            except Exception as e:
                self.on_task_error(name, e)
                succeeded = False
            finally:
                with self._lock:
                    self._current = None
                    self._completed.append((task_id, name, succeeded, time.monotonic()))
                self._queue.task_done()


class AsyncTaskTracker:
    """Track tasks that are running concurrently, outside of any queue."""

    def __init__(self):
        self._running: dict[str, tuple[str, float]] = {}
        self._completed: list[tuple[str, str, bool, float]] = []
        self._lock = threading.Lock()

    def start(self, name: str) -> str:
        task_id = str(uuid.uuid4())
        with self._lock:
            self._running[task_id] = (name, time.monotonic())
        return task_id

    def finish(self, task_id: str, succeeded: bool = True) -> None:
        with self._lock:
            entry = self._running.pop(task_id, None)
            if entry is not None:
                name, _start = entry
                self._completed.append((task_id, name, succeeded, time.monotonic()))

    def get_running(self) -> list[tuple[str, str, float]]:
        """Return (task_id, name, start_time) for each task currently running."""
        with self._lock:
            return [(tid, name, start) for tid, (name, start) in self._running.items()]

    def get_completed(self) -> list[tuple[str, str, bool, float]]:
        """Return (task_id, name, succeeded, finish_time) for each finished task, oldest first."""
        with self._lock:
            return list(self._completed)

    def clear_completed(self) -> None:
        with self._lock:
            self._completed = []
