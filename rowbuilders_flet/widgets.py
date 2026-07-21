"""Flet checkbox row builder, mirroring rowbuilders/widgets.py's CheckBox."""
from typing import Optional

import flet as ft


class FletCheckBox:
    """A row with a checkbox. No None/Default state — matches CheckBox's existing asymmetry."""
    valid_types: tuple[type, ...] = (bool,)

    def __init__(self, default: Optional[bool] = None, **kwargs):
        self.value: bool = bool(default)
        self.checkbox: Optional[ft.Checkbox] = None

    @property
    def cast_value(self) -> bool:
        return self.value

    def pull_value(self) -> None:
        if self.checkbox is not None:
            self.value = bool(self.checkbox.value)

    def build(self, label_width: Optional[int] = None) -> ft.Control:
        self.checkbox = ft.Checkbox(value=self.value)
        return self.checkbox
