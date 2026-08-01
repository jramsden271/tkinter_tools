import tkinter as tk
from styles import apply_style, get_button_style, SPACING
from helpers.task_queue import TaskQueue, AsyncTaskTracker
from helpers.task_item_widget import TaskItemWidget


class TasksWindow:
    def __init__(
        self,
        parent: tk.Tk | tk.Toplevel,
        task_queue: TaskQueue,
        async_tracker: AsyncTaskTracker,
        style: str = "light",
    ):
        self._task_queue = task_queue
        self._async_tracker = async_tracker
        self._style = style

        self.window = tk.Toplevel(parent)
        self.window.title("Tasks")
        self.window.geometry("420x640")
        self.window.resizable(True, True)
        apply_style(self.window, style=style)

        bg = self.window.cget("bg")

        header_frame = tk.Frame(self.window, bg=bg)
        header_frame.pack(fill="x", padx=SPACING["padding"], pady=(SPACING["padding"], 4))

        header = tk.Label(
            header_frame,
            text="Queued",
            font=("Segoe UI", 14, "bold"),
            anchor="w",
        )
        header.pack(side="left", fill="x", expand=True)

        tk.Button(
            header_frame,
            text="Clear Queue",
            command=self._task_queue.cancel_all,
            **get_button_style(self._style),
        ).pack(side="right")

        self._list_frame = tk.Frame(self.window, bg=bg)
        self._list_frame.pack(fill="both", expand=True, padx=SPACING["padding"], pady=(0, SPACING["padding"]))

        running_header = tk.Label(
            self.window,
            text="Running (Async)",
            font=("Segoe UI", 14, "bold"),
            anchor="w",
        )
        running_header.pack(fill="x", padx=SPACING["padding"], pady=(0, 4))

        self._running_frame = tk.Frame(self.window, bg=bg)
        self._running_frame.pack(fill="both", expand=True, padx=SPACING["padding"], pady=(0, SPACING["padding"]))

        completed_header_frame = tk.Frame(self.window, bg=bg)
        completed_header_frame.pack(fill="x", padx=SPACING["padding"], pady=(0, 4))

        completed_header = tk.Label(
            completed_header_frame,
            text="Completed",
            font=("Segoe UI", 14, "bold"),
            anchor="w",
        )
        completed_header.pack(side="left", fill="x", expand=True)

        tk.Button(
            completed_header_frame,
            text="Clear",
            command=self._clear_completed,
            **get_button_style(self._style),
        ).pack(side="right")

        self._completed_frame = tk.Frame(self.window, bg=bg)
        self._completed_frame.pack(fill="both", expand=True, padx=SPACING["padding"], pady=(0, SPACING["padding"]))

        self._refresh()

    def _clear_completed(self) -> None:
        self._task_queue.clear_completed()
        self._async_tracker.clear_completed()

    def _fill_section(self, frame: tk.Frame, entries: list, empty_text: str) -> None:
        for widget in frame.winfo_children():
            widget.destroy()

        if not entries:
            tk.Label(
                frame,
                text=empty_text,
                anchor="center",
                fg="#757575",
            ).pack(expand=True)
            return

        for record, on_cancel in entries:
            item = TaskItemWidget(frame, record, style=self._style, on_cancel=on_cancel)
            item.pack(fill="x", pady=(0, 4))

    def _refresh(self) -> None:
        if not self.window.winfo_exists():
            return

        current = self._task_queue.get_current()
        pending = self._task_queue.get_pending()
        queued_entries = ([(current, None)] if current else []) + [
            (record, self._task_queue.cancel) for record in pending
        ]
        self._fill_section(self._list_frame, queued_entries, "Queue is empty")

        running = sorted(self._async_tracker.get_running(), key=lambda r: r.started_at or 0)
        self._fill_section(self._running_frame, [(r, None) for r in running], "No tasks running asynchronously")

        completed = sorted(
            [*self._task_queue.get_completed(), *self._async_tracker.get_completed()],
            key=lambda r: r.finished_at or 0,
        )
        self._fill_section(self._completed_frame, [(r, None) for r in completed], "No completed tasks")

        self.window.after(200, self._refresh)
