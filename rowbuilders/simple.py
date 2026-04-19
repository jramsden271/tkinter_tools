"""Simple row builders for displaying static content."""
import tkinter as tk
from .abstract import Row


class Text(Row):
    """A row that displays static text."""

    def __init__(self, label: str, id: str = "", **kwargs):
        self.label = label
        self.id = id
        self.kwargs = kwargs

    def build(self, root: tk.Tk, row: int, **kwargs):
        self.kwargs = {**self.kwargs, **kwargs}
        self.label_obj = tk.Label(root, text=self.label)
        self.label_obj.grid(row=row, column=0, sticky="", columnspan=2, **self._default_padding(**self.kwargs))
