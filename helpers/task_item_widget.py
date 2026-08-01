import time
import tkinter as tk
from typing import Callable, Optional

from styles import get_button_style
from styles.light import LightStyle
from styles.dark import DarkStyle
from helpers.task_queue import TaskRecord


def _format_clock(epoch_seconds: float) -> str:
    return time.strftime("%H:%M:%S", time.localtime(epoch_seconds))


def _colors_for(style: str) -> dict:
    return (DarkStyle() if style == "dark" else LightStyle()).colors


class TaskItemWidget(tk.Frame):
    """A compact, three-line summary of one task: title (+ optional Cancel button),
    overridden parameters, and queued/running/completed timing."""

    def __init__(
        self,
        parent: tk.Widget,
        record: TaskRecord,
        style: str = "light",
        on_cancel: Optional[Callable[[str], None]] = None,
    ):
        colors = _colors_for(style)
        bg = parent.cget("bg") if isinstance(parent, (tk.Frame, tk.Toplevel, tk.Tk)) else None
        super().__init__(parent, bg=bg, highlightthickness=1, highlightbackground=colors["border"])

        title_row = tk.Frame(self, bg=bg)
        title_row.pack(fill="x", padx=6, pady=(4, 0))

        tk.Label(
            title_row,
            text=record.name,
            font=("Segoe UI", 10, "bold"),
            bg=bg,
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        if on_cancel is not None:
            tk.Button(
                title_row,
                text="Cancel",
                command=lambda: on_cancel(record.task_id),
                **get_button_style(style),
            ).pack(side="right")
        elif record.finished_at is not None:
            tk.Label(
                title_row,
                text="Done" if record.succeeded else "Error",
                font=("Segoe UI", 9, "bold"),
                fg=colors["success"] if record.succeeded else colors["error"],
                bg=bg,
                anchor="e",
            ).pack(side="right")

        tk.Label(
            self,
            text=record.params or "(defaults only)",
            font=("Segoe UI", 9),
            fg=colors["text_secondary"],
            bg=bg,
            anchor="w",
            justify="left",
            wraplength=360,
        ).pack(fill="x", padx=6)

        tk.Label(
            self,
            text=self._format_times(record),
            font=("Segoe UI", 8),
            fg=colors["text_secondary"],
            bg=bg,
            anchor="w",
        ).pack(fill="x", padx=6, pady=(0, 4))

    @staticmethod
    def _format_times(record: TaskRecord) -> str:
        now = time.time()

        if record.finished_at is not None:
            duration = int(record.finished_at - (record.started_at or record.finished_at))
            return f"Completed {_format_clock(record.finished_at)} · took {duration}s"

        if record.started_at is not None:
            elapsed = int(now - record.started_at)
            return f"Started {_format_clock(record.started_at)} · running {elapsed}s"

        if record.queued_at is not None:
            return f"Queued at {_format_clock(record.queued_at)}"

        return ""
