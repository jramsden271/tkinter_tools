"""Entry-based row builders for text input."""
import tkinter as tk
from tkinter import filedialog
from abc import abstractmethod, ABC
from typing import Optional, Callable
import regex
from pathlib import Path
from .abstract import ValueRow


class Entry(ValueRow, ABC):
    """A generic row with a text entry field."""
    entry_obj: Optional[tk.Entry] = None

    def __init__(self, id: str = "", **kwargs):
        self.id = id
        self.kwargs = kwargs

    @property
    def cast_value(self):
        return self.value if self.value else None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    def _get_validator(self) -> None | Callable:
        """Get validation function for this entry. Override in subclasses."""
        return None

    def push_value(self):
        """Push the current value to the entry widget."""
        if self.entry_obj and self.value:
            self.entry_obj.delete(0, tk.END)
            self.entry_obj.insert(0, str(self.value))

    def pull_value(self):
        """Pull the value from the entry widget."""
        if self.entry_obj:
            self.value = self.entry_obj.get()

    def build(self, root: tk.Tk, row: int):
        self.label_obj = tk.Label(root, text=self.label)
        self.label_obj.grid(row=row, column=0, sticky="W", **self._default_padding(**self.kwargs))

        self.entry_obj = tk.Entry(root, width=self.kwargs.get("width") or self._WIDTH)

        if validator := self._get_validator():
            self.entry_obj.config(
                validate="key",
                validatecommand=(root.register(validator), '%P')
            )
        self.entry_obj.grid(row=row, column=1, sticky="EW", **self._default_padding(**self.kwargs))
        self.push_value()


class TextEntry(Entry):
    """A row with a text entry field for string values."""
    pass


class FloatEntry(Entry):
    """A row with a float entry field."""

    def _get_validator(self):
        return lambda v: regex.fullmatch(r"-?\d*\.?\d*", v) is not None

    @property
    def cast_value(self) -> Optional[float]:
        try:
            return float(self.value) if self.value else None
        except:
            return None


class IntEntry(Entry):
    """A row with an integer entry field."""

    def _get_validator(self):
        return lambda v: not v or v.isdigit()

    @property
    def cast_value(self) -> int | None:
        try:
            return int(self.value) if self.value else None
        except:
            return None


class PathEntry(Entry):
    """A row with a path/file selector."""
    button_obj: Optional[tk.Button] = None

    def __init__(self, id: str = "", allow_directory: bool = True, allow_file: bool = True, **kwargs):
        super().__init__(id=id, **kwargs)
        self.allow_directory = allow_directory
        self.allow_file = allow_file

    def _on_browse_click(self):
        """Open a file/folder selection dialog and update the entry."""
        if self.allow_directory and not self.allow_file:
            path = filedialog.askdirectory()
        elif self.allow_file and not self.allow_directory:
            path = filedialog.askopenfilename()
        else:
            # Default: allow selection of files (user can see folders in navigation)
            path = filedialog.askopenfilename()

        if path:
            self.value = path
            if self.entry_obj:
                self.entry_obj.delete(0, tk.END)
                self.entry_obj.insert(0, path)

    def _get_validator(self) -> None | Callable:
        return None

    def build(self, root: tk.Tk, row: int):
        self.label_obj = tk.Label(root, text=self.label)
        self.label_obj.grid(row=row, column=0, sticky="W", **self._default_padding(**self.kwargs))

        # Create a frame to hold entry and button side by side
        frame = tk.Frame(root)
        frame.grid(row=row, column=1, sticky="EW", **self._default_padding(**self.kwargs))

        self.entry_obj = tk.Entry(frame, width=self.kwargs.get("width") or self._WIDTH)
        self.entry_obj.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.button_obj = tk.Button(frame, text="Browse...", command=self._on_browse_click)
        self.button_obj.pack(side=tk.RIGHT, padx=(5, 0))

        self.push_value()

    @property
    def cast_value(self) -> Optional[Path]:
        try:
            return Path(self.value) if self.value else None
        except:
            return None
