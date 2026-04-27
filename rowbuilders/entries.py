"""Entry-based row builders for text input."""
import tkinter as tk
from tkinter import ttk, filedialog
from abc import abstractmethod, ABC
from typing import List, Optional, Callable
import regex
from pathlib import Path
from .abstract import ValueRow
import tk_extension
from .abstract import inc_optional


@abstractmethod
class Entry(ValueRow, ABC):
    """A generic row with a text entry field."""
    entry_obj: Optional[tk.Entry] = None

    def __init__(self, can_be_none: bool = False, has_default: bool = False, default: Optional[str] = None, id: str = "", **kwargs):
        self.kwargs = kwargs
        self.id = id
        self.can_be_none = can_be_none
        self.has_default = has_default
        self.default = default

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

    def _on_entry_changed(self, *_):
        if not getattr(self, '_updating', False) and hasattr(self, 'combo_obj'):
            values = list(self.combo_obj.cget("values"))
            if "Current" in values:
                self.combo_obj.set("Current")

    def _on_combo_selected(self, _=None):
        if self.entry_obj and self.combo_obj.get().startswith("Default:") and self.default is not None:
            self._updating = True
            self.entry_obj.delete(0, tk.END)
            self.entry_obj.insert(0, str(self.default))
            self._updating = False

    def push_value(self):
        """Push the current value to the entry widget."""
        if self.entry_obj and self.value:
            self.entry_obj.delete(0, tk.END)
            self.entry_obj.insert(0, str(self.value))

    def pull_value(self):
        """Pull the value from the entry widget."""
        if self.entry_obj:
            if self.combo_obj.get() == "None":
                self.value = None
            elif self.combo_obj.get().startswith("Default:"):
                self.value = self.default
            else:
                self.value = self.entry_obj.get()

    def build(self, root: tk.Tk, row: int, additional_widgets: List[Callable[[tk.Frame], tk.Widget]] = [], **kwargs):
        self.label_obj = tk.Label(root, text=self.label)
        self.label_obj.grid(row=row, column=0, sticky="W", **self._default_padding(**self.kwargs))

        # Create a frame to hold entry and button side by side
        frame = tk.Frame(root)
        frame.grid(row=row, column=1, sticky="EW", **self._default_padding(**self.kwargs))

        self._entry_var = tk.StringVar()
        self.entry_obj = tk_extension.Entry(frame, textvariable=self._entry_var, width=self.kwargs.get("width") or self._WIDTH)
        self.entry_obj.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._entry_var.trace_add("write", self._on_entry_changed)

        values = []
        if self.has_default:
            values.append(f"Default: {self.default}")
        values.append("Current")
        if self.can_be_none:
            values.append("None")

        self.combo_obj = ttk.Combobox(frame, values=values, state="readonly", width=12)
        self.combo_obj.current(0)
        self.combo_obj.bind("<<ComboboxSelected>>", self._on_combo_selected)
        if len(values) > 1:
            self.combo_obj.pack(side=tk.RIGHT, padx=(5, 0))

        for widget_factory in additional_widgets:
            widget_factory(frame).pack(side=tk.RIGHT, padx=(5, 0))
               

        if validator := self._get_validator():
            self.entry_obj.config(
                validate="key",
                validatecommand=(root.register(validator), '%P')
            )


class TextEntry(Entry):
    """A row with a text entry field for string values."""
    valid_types: tuple[type, ...] = (*inc_optional(str),)


class FloatEntry(Entry):
    """A row with a float entry field."""
    valid_types: tuple[type, ...] = (*inc_optional(float),)

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
    valid_types: tuple[type, ...] = (*inc_optional(int),)

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
    valid_types: tuple[type, ...] = (*inc_optional(Path),)

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

    def build(self, root: tk.Tk, row: int, additional_widgets: List[Callable[[tk.Frame], tk.Widget]] = [], **kwargs):
        super().build(root, row, additional_widgets=[
            lambda frame: tk.Button(frame, text="Browse...", command=self._on_browse_click),
            *additional_widgets,
        ], **kwargs)

    @property
    def cast_value(self) -> Optional[Path]:
        try:
            return Path(self.value) if self.value else None
        except:
            return None
