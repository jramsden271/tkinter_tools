"""Specialized widget row builders."""
import tkinter as tk
from typing import Optional
from .abstract import ValueRow


class CheckBox(ValueRow):
    """A row with a checkbox widget."""
    checkbox_obj: Optional[tk.Checkbutton] = None
    _checkbox_var: Optional[tk.BooleanVar] = None
    valid_types: tuple[type, ...] = (bool,)

    def __init__(self, id: str = "", **kwargs):
        self.id = id
        self.kwargs = kwargs
        self._value = False

    @property
    def cast_value(self) -> bool:
        return self.value

    @property
    def value(self) -> bool:
        return bool(self._value)

    @value.setter
    def value(self, val: bool):
        self._value = val

    def push_value(self):
        """Push the current value to the checkbox widget."""
        if self._checkbox_var:
            self._checkbox_var.set(self.value)

    def pull_value(self):
        """Pull the value from the checkbox widget."""
        if self._checkbox_var:
            self.value = self._checkbox_var.get()

    def build(self, root: tk.Tk, label_width: Optional[int] = None, **kwargs) -> tk.Frame:
        row_frame = tk.Frame(root)

        label_opts = {"width": label_width, "anchor": "w"} if label_width else {}
        self.label_obj = tk.Label(row_frame, text=self.label, **label_opts)
        self.label_obj.pack(side=tk.LEFT, **self._default_padding(**self.kwargs))

        self._checkbox_var = tk.BooleanVar(value=self.value)
        self.checkbox_obj = tk.Checkbutton(row_frame, variable=self._checkbox_var)
        self.checkbox_obj.pack(side=tk.LEFT, **self._default_padding(**self.kwargs))
        self.push_value()
        return row_frame
