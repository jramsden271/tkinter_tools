"""Tasks dialog: shows the sync queue (current + pending) and running async tasks.

Unlike the Help dialog, this needs live polling while open — the caller's
status-poll loop should call refresh() each tick if is_open is True.
"""
import time

import flet as ft

from helpers.task_queue import TaskQueue, AsyncTaskTracker


class TasksDialog:
    def __init__(self, task_queue: TaskQueue, async_tracker: AsyncTaskTracker, on_close):
        self.task_queue = task_queue
        self.async_tracker = async_tracker
        self.is_open = False

        self._queue_column = ft.Column([])
        self._running_column = ft.Column([])

        self.dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Text("Tasks"),
                    ft.TextButton("Clear Queue", on_click=lambda e: self.task_queue.cancel_all()),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            content=ft.Column(
                [
                    ft.Text("Queued / Running", weight=ft.FontWeight.BOLD),
                    self._queue_column,
                    ft.Text("Running (Async)", weight=ft.FontWeight.BOLD),
                    self._running_column,
                ],
                tight=True,
                scroll=ft.ScrollMode.AUTO,
                width=400,
            ),
            actions=[ft.TextButton("Close", on_click=on_close)],
            on_dismiss=lambda e: self._on_dismiss(),
        )

    def _on_dismiss(self) -> None:
        self.is_open = False

    def refresh(self) -> None:
        now = time.monotonic()

        current = self.task_queue.get_current()
        pending = self.task_queue.get_pending()

        queue_rows = []
        if not current and not pending:
            queue_rows.append(ft.Text("Queue is empty", color=ft.Colors.GREY))
        else:
            if current:
                _tid, name, start_time = current
                elapsed = int(now - start_time)
                queue_rows.append(
                    ft.Row(
                        [ft.Text(name, expand=True), ft.Text(f"{elapsed}s")],
                    )
                )
            for task_id, name in pending:
                queue_rows.append(
                    ft.Row(
                        [
                            ft.Text(name, expand=True),
                            ft.TextButton("Cancel", on_click=lambda e, tid=task_id: self.task_queue.cancel(tid)),
                        ]
                    )
                )
        self._queue_column.controls = queue_rows
        self._safe_update(self._queue_column)

        running = self.async_tracker.get_running()
        running_rows = []
        if not running:
            running_rows.append(ft.Text("No tasks running asynchronously", color=ft.Colors.GREY))
        else:
            for _tid, name, start_time in sorted(running, key=lambda t: t[2]):
                elapsed = int(now - start_time)
                running_rows.append(
                    ft.Row([ft.Text(name, expand=True), ft.Text(f"{elapsed}s")])
                )
        self._running_column.controls = running_rows
        self._safe_update(self._running_column)

    @staticmethod
    def _safe_update(control: ft.Control) -> None:
        """Update a control if it's currently attached to a page, no-op otherwise."""
        try:
            control.update()
        except RuntimeError:
            pass
