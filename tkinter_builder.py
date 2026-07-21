from time import sleep
import threading
import time
import tkinter as tk
from typing import Callable, Literal, Optional, Any
from core.method_collection import MethodCollection
from helpers.conjugator import Conjugator
from helpers.task_queue import TaskQueue
from rowbuilders import Text
from pathlib import Path
from styles import apply_style, get_button_style, COLORS, FONTS, SPACING
from help_window import HelpWindow
from helpers.queue_window import QueueWindow

from tkinter import messagebox


class Spinner:
    def __init__(self, parent):
        self.label = tk.Label(parent, text="", width=1)
        self.chars = ['|', '/', '-', '\\']
        self.index = 0
        self.after_id = None

    def start(self):
        self._animate()

    def _animate(self):
        self.label.config(text=self.chars[self.index % len(self.chars)])
        self.index += 1
        self.after_id = self.label.after(100, self._animate)

    def stop(self):
        if self.after_id:
            self.label.after_cancel(self.after_id)
        self.label.config(text="")


class TKinterInput:

    def __init__(
        self,
        methods: Callable | list[Callable],
        root: Optional[tk.Tk] = None,
        keep_on_top: bool = False,
        style: str = "light",
    ):
        self.method_collection = MethodCollection(methods)
        self.style = style

        if root:
            self.root = root
        else:
            self.root = tk.Tk()

        self.root.title(self.method_collection.title)

        # Apply modern styling before building widgets so labels, entries, and buttons inherit theme defaults.
        apply_style(self.root, style=self.style)

        max_label_width = 0
        for para in self.method_collection.parameter_states:
            if para.rowbuilder:
                desc = self.method_collection.get_parameter_description(para.name)
                text = para.get_label_text(desc)
                max_label_width = max(max_label_width, max(int(len(line)*0.8) for line in text.split('\n')))

        for para in self.method_collection.parameter_states:
            if para.rowbuilder:
                description = self.method_collection.get_parameter_description(
                    para.name
                )
                frame = para.build(self.root, param_description=description, label_width=max_label_width)
                if frame:
                    frame.pack(fill=tk.X, padx=SPACING["padding"])

        button_frame = tk.Frame(self.root, bg=self.root.cget("bg"))
        button_frame.pack(
            fill=tk.X,
            pady=SPACING["button_pady"],
            padx=SPACING["padding"],
        )

        status_frame = tk.Frame(self.root, bg=self.root.cget("bg"))
        status_frame.pack(
            fill=tk.X,
            padx=SPACING["padding"],
            pady=(0, SPACING["button_pady"]),
        )



        def open_queue_window():
            if _queue_window and _queue_window[0].window.winfo_exists():
                _queue_window[0].window.lift()
                return
            win = QueueWindow(self.root, task_queue, self.style)
            _queue_window.clear()
            _queue_window.append(win)

        queue_btn = tk.Button(
            status_frame,
            text="Queue",
            command=open_queue_window,
        )
        queue_btn.pack(side="left", padx=(0, 5))

        spinner = Spinner(status_frame)
        spinner.label.pack(side="left", padx=(0, 5))

        status_label = tk.Label(status_frame, text="", anchor="w")
        status_label.pack(side="left", fill="x", expand=True)

        _task_start: list[float | None] = [None]

        def _tick_elapsed(label: str) -> None:
            if _task_start[0] is None:
                return
            elapsed = int(time.monotonic() - _task_start[0])
            status_label.config(text=f"Running: {label}... ({elapsed}s)")
            status_label.after(1000, lambda: _tick_elapsed(label))

        def on_task_start(name: str) -> None:
            conjugated = Conjugator(name)
            label = conjugated.to_present_continuous().capitalize()
            def _():
                _task_start[0] = time.monotonic()
                spinner.start()
                status_label.config(text=f"Running: {label}... (0s)")
                status_label.after(1000, lambda: _tick_elapsed(label))
            status_label.after(0, _)

        def on_task_complete(name: str) -> None:
            conjugated = Conjugator(name)
            def _():
                elapsed = round(time.monotonic() - _task_start[0],3) if _task_start[0] is not None else 0
                _task_start[0] = None
                spinner.stop()
                status_label.config(text=f"Completed: {conjugated.to_past().capitalize()} ({elapsed}s)")
            status_label.after(0, _)

        def on_task_error(name: str, e: Exception) -> None:
            def _():
                elapsed = round(time.monotonic() - _task_start[0],3) if _task_start[0] is not None else 0
                _task_start[0] = None
                spinner.stop()
                status_label.config(text=f"Error in {name} after {elapsed}s")
                messagebox.showerror("Error", str(e))
            status_label.after(0, _)

        task_queue = TaskQueue(on_task_start, on_task_complete, on_task_error)

        def run_async(method) -> None:
            """Run a method in its own thread immediately, bypassing the queue."""
            action = self.method_collection.create_submit_action(method)

            def _worker():
                try:
                    action()
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

            threading.Thread(target=_worker, daemon=True).start()

        _queue_window: list[QueueWindow] = []



        def update_queue_btn():
            count = len(task_queue.get_pending())
            queue_btn.config(text=f"Queue ({count})" if count else "Queue")
            queue_btn.after(200, update_queue_btn)

        update_queue_btn()

        #for method in [methods_[i] for i in range(len(methods_)-1, -1, -1)]:
        for i in range(len(self.method_collection.methods)):
            method = self.method_collection.methods[i]

            btn = tk.Button(
                button_frame,
                text=f"{method.formatted_title} (F{i + 1})",
                command=lambda m=method, n=method.formatted_title: task_queue.submit(self.method_collection.create_submit_action(m), n),
            )
            btn.pack(side="right", padx=(5, 0))

            menu = tk.Menu(button_frame, tearoff=0)
            menu.add_command(
                label="Run",
                command=lambda m=method, n=method.formatted_title: task_queue.submit(self.method_collection.create_submit_action(m), n),
            )
            menu.add_command(
                label="Run Asynchronously",
                command=lambda m=method: run_async(m),
            )
            menu.add_separator()
            menu.add_command(
                label="Help",
                command=lambda m=method: HelpWindow(
                    self.root,
                    f"Help: {m.formatted_title}",
                    m.get_help_text(),
                    self.style,
                ),
            )
            btn.bind("<Button-3>", lambda e, m=menu: m.tk_popup(e.x_root, e.y_root))

        for i, method in enumerate(self.method_collection.methods):
            self.root.bind(
                f"<F{i + 1}>",
                lambda _, m=method, n=method.formatted_title: task_queue.submit(self.method_collection.create_submit_action(m), n),
            )

        if keep_on_top:
            self.root.attributes("-topmost", True)

        self.root.mainloop()


if __name__ == "__main__":

    def test_method_123(
        id: int,
        rate: float,
        name: str,
        some_path: Path|None = None,
        is_active: bool = False,
        another_default: int = 123,
        another: str = "asdf",
        floaty: float|None = 1.23,
        #moreee: Literal["option1", "option2"] = "option1",
        *args123,
        **kwargs,
    ):
        """
        Docstring for test_method_123

        :param id: Description
        :type id: int
        :param rate: Description
        :type rate: float
        :param name: Description
        :param is_active: Description
        :type is_active: bool
        :param args123: Description
        :param kwargs: Description
        """
        print(
            f"ID: {id}, Rate: {rate}, Name: {name}, Path: {some_path}, Active: {is_active}, Another Default: {another_default}, Another: {another}, Floaty: {floaty}"
        )

    def test_method_456(
        name: str | None, age: int = 30
    ):
        sleep(10)  # Simulate a long-running task
        raise Exception("This is a test exception for demonstration purposes.")
    
    def run_a_test_thing():
        sleep(5)  # Simulate a long-running task

    TKinterInput([test_method_123, test_method_456, run_a_test_thing], style="dark")
