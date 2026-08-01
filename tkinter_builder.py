from time import sleep
import threading
import time
import tkinter as tk
from typing import Callable, Literal, Optional, Any
from core.method_collection import MethodCollection
from helpers.conjugator import Conjugator
from helpers.task_queue import TaskQueue, AsyncTaskTracker
from rowbuilders import Text
from pathlib import Path
from styles import apply_style, get_button_style, COLORS, FONTS, SPACING
from help_window import HelpWindow
from helpers.tasks_window import TasksWindow

from tkinter import messagebox


class Spinner:
    def __init__(self, parent):
        self.label = tk.Label(parent, text="", width=1)
        self.chars = ['|', '/', '-', '\\']
        self.index = 0
        self.after_id = None

    def start(self):
        if self.after_id is not None:
            return
        self._animate()

    def _animate(self):
        self.label.config(text=self.chars[self.index % len(self.chars)])
        self.index += 1
        self.after_id = self.label.after(100, self._animate)

    def stop(self):
        if self.after_id:
            self.label.after_cancel(self.after_id)
            self.after_id = None
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



        def open_tasks_window():
            if _tasks_window and _tasks_window[0].window.winfo_exists():
                _tasks_window[0].window.lift()
                return
            win = TasksWindow(self.root, task_queue, async_tracker, self.style)
            _tasks_window.clear()
            _tasks_window.append(win)

        tasks_btn = tk.Button(
            status_frame,
            text="Tasks",
            command=open_tasks_window,
        )
        tasks_btn.pack(side="left", padx=(0, 5))

        spinner = Spinner(status_frame)
        spinner.label.pack(side="left", padx=(0, 5))

        status_label = tk.Label(status_frame, text="", anchor="w")
        status_label.pack(side="left", fill="x", expand=True)

        def on_task_complete(name: str) -> None:
            conjugated = Conjugator(name)
            def _():
                status_label.config(text=f"Completed: {conjugated.to_past().capitalize()}")
            status_label.after(0, _)

        def on_task_error(name: str, e: Exception) -> None:
            def _():
                status_label.config(text=f"Error in {name}")
                messagebox.showerror("Error", str(e))
            status_label.after(0, _)

        task_queue = TaskQueue(lambda name: None, on_task_complete, on_task_error)
        async_tracker = AsyncTaskTracker()

        def submit_method(method) -> None:
            """Snapshot the current form values and enqueue a run of this method."""
            action, params = self.method_collection.create_submit_action_with_summary(method)
            task_queue.submit(action, method.formatted_title, params)

        def run_async(method) -> None:
            """Run a method in its own thread immediately, bypassing the queue."""
            action, params = self.method_collection.create_submit_action_with_summary(method)
            task_id = async_tracker.start(method.formatted_title, params)

            def _worker():
                succeeded = True
                try:
                    action()
                except Exception as e:
                    succeeded = False
                    self.root.after(0, lambda e=e: messagebox.showerror("Error", str(e)))
                finally:
                    async_tracker.finish(task_id, succeeded)

            threading.Thread(target=_worker, daemon=True).start()

        _tasks_window: list[TasksWindow] = []

        def update_status() -> None:
            current = task_queue.get_current()
            running_async = async_tracker.get_running()
            total_running = (1 if current else 0) + len(running_async)

            pending_count = len(task_queue.get_pending())
            tasks_btn.config(
                text=f"Tasks ({pending_count + total_running})" if pending_count + total_running else "Tasks"
            )

            if total_running == 0:
                spinner.stop()
            elif total_running == 1:
                spinner.start()
                record = current if current else running_async[0]
                conjugated = Conjugator(record.name)
                label = conjugated.to_present_continuous().capitalize()
                elapsed = int(time.time() - record.started_at) if record.started_at else 0
                status_label.config(text=f"Running: {label}... ({elapsed}s)")
            else:
                spinner.start()
                status_label.config(text=f"{total_running} tasks running...")

            status_label.after(200, update_status)

        update_status()

        buttons_frame = tk.Frame(button_frame, bg=self.root.cget("bg"))
        buttons_frame.pack(side="right")

        for i in range(len(self.method_collection.methods)):
            method = self.method_collection.methods[i]

            btn = tk.Button(
                buttons_frame,
                text=f"{method.formatted_title} (F{i + 1})",
                command=lambda m=method: submit_method(m),
            )
            btn.pack(side="left", padx=(5, 0))

            menu = tk.Menu(buttons_frame, tearoff=0)
            menu.add_command(
                label="Run",
                command=lambda m=method: submit_method(m),
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
                    m.help_rows(),
                    self.style,
                    summary=m.summary,
                    notes=m.help_notes(),
                ),
            )
            btn.bind("<Button-3>", lambda e, m=menu: m.tk_popup(e.x_root, e.y_root))

        for i, method in enumerate(self.method_collection.methods):
            self.root.bind(
                f"<F{i + 1}>",
                lambda _, m=method: submit_method(m),
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
