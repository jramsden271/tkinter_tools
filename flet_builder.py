import asyncio
import threading
import time
from pathlib import Path
from typing import Callable, Optional

import flet as ft

from core.method_collection import MethodCollection
from helpers.conjugator import Conjugator
from helpers.task_queue import TaskQueue, AsyncTaskTracker
from rowbuilders_flet import select_flet_rowbuilder
from styles import LightStyle, DarkStyle
from flet_ui.help_dialog import build_help_dialog
from flet_ui.tasks_dialog import TasksDialog


class FletInput:
    def __init__(self, methods: Callable | list[Callable], style: str = "light"):
        self.method_collection = MethodCollection(methods)
        self.style = style
        self._discard_tk_rowbuilders()

        self.task_queue = TaskQueue(
            lambda name: None,
            self._on_task_complete,
            self._on_task_error,
        )
        self.async_tracker = AsyncTaskTracker()

        self._page: Optional[ft.Page] = None
        self._last_status_text = ""
        self._pending_errors: list[str] = []
        self._status_text: Optional[ft.Text] = None
        self._spinner: Optional[ft.ProgressRing] = None
        self._tasks_button: Optional[ft.TextButton] = None
        self._tasks_dialog: Optional[TasksDialog] = None

    def _discard_tk_rowbuilders(self) -> None:
        """Replace the auto-created tkinter rowbuilders with Flet-facing ones.

        ParameterState.__post_init__ always instantiates a tkinter rowbuilder
        via rowbuilders.select_rowbuilder(). MethodCollection.collect_final_args
        only ever calls .pull_value()/.cast_value on whatever lives in
        `rowbuilder`, so reassigning it to a Flet builder here lets the shared
        backend logic work unmodified.
        """
        for param in self.method_collection.parameter_states:
            builder_class = select_flet_rowbuilder(param.annotation)
            if builder_class:
                param.rowbuilder = builder_class(
                    can_be_none=param.can_be_none,
                    has_default=param.has_default,
                    default=param.default_value,
                )
            else:
                param.rowbuilder = None

    def _on_task_complete(self, name: str) -> None:
        conjugated = Conjugator(name)
        self._last_status_text = f"Completed: {conjugated.to_past().capitalize()}"

    def _on_task_error(self, name: str, e: Exception) -> None:
        self._last_status_text = f"Error in {name}"
        self._pending_errors.append(str(e))

    def run(self) -> None:
        ft.run(self._main)

    def _main(self, page: ft.Page) -> None:
        self._page = page
        page.title = self.method_collection.title

        theme_colors = DarkStyle().colors if self.style == "dark" else LightStyle().colors
        page.theme_mode = ft.ThemeMode.DARK if self.style == "dark" else ft.ThemeMode.LIGHT
        page.theme = ft.Theme(color_scheme_seed=theme_colors["accent"])
        page.dark_theme = ft.Theme(color_scheme_seed=DarkStyle().colors["accent"])

        max_label_width = self._compute_max_label_width()

        param_rows = []
        for param in self.method_collection.parameter_states:
            if not param.rowbuilder:
                continue
            description = self.method_collection.get_parameter_description(param.name)
            label_text = param.get_label_text(description)
            control = param.rowbuilder.build(label_width=max_label_width)
            param_rows.append(
                ft.Row(
                    [ft.Text(label_text, width=max_label_width), control],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                )
            )

        method_buttons = [
            self._build_method_button(method, i)
            for i, method in enumerate(self.method_collection.methods)
        ]

        self._status_text = ft.Text("")
        self._spinner = ft.ProgressRing(width=16, height=16, stroke_width=2, visible=False)
        self._tasks_button = ft.TextButton("Tasks", on_click=self._open_tasks_dialog)
        self._tasks_dialog = TasksDialog(self.task_queue, self.async_tracker, on_close=self._close_dialog)

        status_bar = ft.Row([self._tasks_button, self._spinner, self._status_text])

        page.add(
            ft.Column(param_rows),
            ft.Row(method_buttons, alignment=ft.MainAxisAlignment.END),
            status_bar,
        )

        page.on_keyboard_event = self._on_keyboard_event
        page.run_task(self._status_poll_loop)

    def _build_method_button(self, method, index: int) -> ft.Control:
        button = ft.Button(
            content=f"{method.formatted_title} (F{index + 1})",
            on_click=lambda e, m=method: self._on_run_clicked(m),
        )
        return ft.ContextMenu(
            content=button,
            secondary_items=[
                ft.PopupMenuItem("Run", on_click=lambda e, m=method: self._on_run_clicked(m)),
                ft.PopupMenuItem("Run Asynchronously", on_click=lambda e, m=method: self._run_async(m)),
                ft.PopupMenuItem("Help", on_click=lambda e, m=method: self._open_help_dialog(m)),
            ],
        )

    def _on_keyboard_event(self, e: ft.KeyboardEvent) -> None:
        if not e.key.startswith("F") or not e.key[1:].isdigit():
            return
        index = int(e.key[1:]) - 1
        methods = self.method_collection.methods
        if 0 <= index < len(methods):
            self._on_run_clicked(methods[index])

    def _run_async(self, method) -> None:
        """Run a method on its own thread immediately, bypassing the queue."""
        action = self.method_collection.create_submit_action(method)
        task_id = self.async_tracker.start(method.formatted_title)

        def _worker():
            try:
                action()
            except Exception as e:
                self._pending_errors.append(str(e))
            finally:
                self.async_tracker.finish(task_id)

        threading.Thread(target=_worker, daemon=True).start()

    def _open_help_dialog(self, method) -> None:
        dialog = build_help_dialog(method, on_close=self._close_dialog)
        self._page.show_dialog(dialog)

    def _open_tasks_dialog(self, e=None) -> None:
        self._tasks_dialog.is_open = True
        self._tasks_dialog.refresh()
        self._page.show_dialog(self._tasks_dialog.dialog)

    def _close_dialog(self, e=None) -> None:
        self._page.pop_dialog()

    def _compute_max_label_width(self) -> int:
        max_label_width = 0
        for param in self.method_collection.parameter_states:
            if not param.rowbuilder:
                continue
            description = self.method_collection.get_parameter_description(param.name)
            text = param.get_label_text(description)
            max_label_width = max(max_label_width, max(int(len(line) * 7) for line in text.split("\n")))
        return max_label_width

    def _on_run_clicked(self, method) -> None:
        action = self.method_collection.create_submit_action(method)
        self.task_queue.submit(action, method.formatted_title)

    async def _status_poll_loop(self) -> None:
        while True:
            self._refresh_status_ui()
            await asyncio.sleep(0.25)

    def _refresh_status_ui(self) -> None:
        if self._page is None:
            return

        current = self.task_queue.get_current()
        running_async = self.async_tracker.get_running()
        total_running = (1 if current else 0) + len(running_async)

        pending_count = len(self.task_queue.get_pending())
        total_count = pending_count + total_running
        self._tasks_button.content = f"Tasks ({total_count})" if total_count else "Tasks"

        if total_running == 0:
            self._spinner.visible = False
            if self._status_text.value != self._last_status_text:
                self._status_text.value = self._last_status_text
        elif total_running == 1:
            self._spinner.visible = True
            if current:
                _tid, name, start_time = current
            else:
                _tid, name, start_time = running_async[0]
            conjugated = Conjugator(name)
            label = conjugated.to_present_continuous().capitalize()
            elapsed = int(time.monotonic() - start_time)
            self._status_text.value = f"Running: {label}... ({elapsed}s)"
        else:
            self._spinner.visible = True
            self._status_text.value = f"{total_running} tasks running..."

        if self._tasks_dialog is not None and self._tasks_dialog.is_open:
            self._tasks_dialog.refresh()

        self._page.update()

        if self._pending_errors:
            message = self._pending_errors.pop(0)
            self._page.show_dialog(
                ft.AlertDialog(
                    title=ft.Text("Error"),
                    content=ft.Text(message),
                    actions=[ft.TextButton("Close", on_click=self._close_dialog)],
                )
            )


if __name__ == "__main__":
    from time import sleep

    def test_method_123(
        id: int,
        rate: float,
        name: str,
        some_path: Path | None = None,
        is_active: bool = False,
        another_default: int = 123,
        another: str = "asdf",
        floaty: float | None = 1.23,
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

    def test_method_456(name: str | None, age: int = 30):
        sleep(10)
        raise Exception("This is a test exception for demonstration purposes.")

    def run_a_test_thing():
        sleep(5)

    FletInput([test_method_123, test_method_456, run_a_test_thing], style="dark").run()
