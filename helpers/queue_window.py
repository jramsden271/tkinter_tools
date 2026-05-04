import tkinter as tk
from styles import apply_style, get_button_style, SPACING
from helpers.task_queue import TaskQueue


class QueueWindow:
    def __init__(self, parent: tk.Tk | tk.Toplevel, task_queue: TaskQueue, style: str = "light"):
        self._task_queue = task_queue
        self._style = style

        self.window = tk.Toplevel(parent)
        self.window.title("Task Queue")
        self.window.geometry("420x320")
        self.window.resizable(True, True)
        apply_style(self.window, style=style)

        bg = self.window.cget("bg")

        header = tk.Label(
            self.window,
            text="Pending Tasks",
            font=("Segoe UI", 14, "bold"),
            anchor="w",
        )
        header.pack(fill="x", padx=SPACING["padding"], pady=(SPACING["padding"], 4))

        self._list_frame = tk.Frame(self.window, bg=bg)
        self._list_frame.pack(fill="both", expand=True, padx=SPACING["padding"], pady=(0, SPACING["padding"]))

        self._refresh()

    def _refresh(self) -> None:
        if not self.window.winfo_exists():
            return

        for widget in self._list_frame.winfo_children():
            widget.destroy()

        pending = self._task_queue.get_pending()
        bg = self.window.cget("bg")

        if not pending:
            tk.Label(
                self._list_frame,
                text="Queue is empty",
                anchor="center",
                fg="#757575",
            ).pack(expand=True)
        else:
            for task_id, name in pending:
                row = tk.Frame(self._list_frame, bg=bg)
                row.pack(fill="x", pady=2)

                tk.Label(
                    row,
                    text=name,
                    anchor="w",
                ).pack(side="left", fill="x", expand=True, padx=(0, 8))

                tk.Button(
                    row,
                    text="Cancel",
                    command=lambda tid=task_id: self._task_queue.cancel(tid),
                    **get_button_style(self._style),
                ).pack(side="right")

        self.window.after(200, self._refresh)
