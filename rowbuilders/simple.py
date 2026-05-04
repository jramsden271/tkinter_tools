"""Simple row builders for displaying static content."""
import tkinter as tk
from typing import Optional
from .abstract import Row


class Text(Row):
    """A row that displays static text."""

    def __init__(self, label: str, id: str = "", **kwargs):
        self.label = label
        self.id = id
        self.kwargs = kwargs

    def build(self, root: tk.Tk, label_width: Optional[int] = None, **kwargs) -> tk.Frame:
        self.kwargs = {**self.kwargs, **kwargs}
        row_frame = tk.Frame(root)
        self.label_obj = tk.Label(row_frame, text=self.label)
        self.label_obj.pack(fill=tk.X, **self._default_padding(**self.kwargs))
        return row_frame
