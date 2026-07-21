"""Flet text-field-based row builders, mirroring rowbuilders/entries.py's Entry hierarchy."""
from pathlib import Path
from typing import Optional

import flet as ft

from .abstract import inc_optional

_DEFAULT_PREFIX = "Default: "
_CURRENT = "Current"
_NONE = "None"


class FletEntry:
    """A row with a text field and a Default/Current/None dropdown, mirroring Entry."""

    def __init__(self, can_be_none: bool = False, has_default: bool = False, default: Optional[str] = None, **kwargs):
        self.can_be_none = can_be_none
        self.has_default = has_default
        self.default = default
        self.value: Optional[str] = None
        self.field: Optional[ft.TextField] = None
        self.dropdown: Optional[ft.Dropdown] = None
        self._updating = False

    def _get_input_filter(self) -> Optional[ft.InputFilter]:
        """Get a keystroke input filter for this entry. Override in subclasses."""
        return None

    def _dropdown_options(self) -> list[str]:
        values = []
        if self.has_default:
            values.append(f"{_DEFAULT_PREFIX}{self.default}")
        values.append(_CURRENT)
        if self.can_be_none:
            values.append(_NONE)
        return values

    def _on_field_changed(self, e: ft.Event) -> None:
        if self._updating or self.dropdown is None:
            return
        if self.dropdown.value != _CURRENT:
            self.dropdown.value = _CURRENT
            self.dropdown.update()

    def _on_dropdown_selected(self, e: ft.Event) -> None:
        if self.field is None or self.dropdown is None:
            return
        if self.dropdown.value == f"{_DEFAULT_PREFIX}{self.default}" and self.default is not None:
            self._updating = True
            self.field.value = str(self.default)
            self.field.update()
            self._updating = False

    def pull_value(self) -> None:
        """Pull the value from the dropdown state, falling back to the field text."""
        if self.field is None:
            return
        if self.dropdown is not None and self.dropdown.value == _NONE:
            self.value = None
        elif self.dropdown is not None and self.dropdown.value == f"{_DEFAULT_PREFIX}{self.default}":
            self.value = self.default
        else:
            self.value = self.field.value

    @property
    def cast_value(self):
        return self.value if self.value else None

    def build(self, label_width: Optional[int] = None) -> ft.Control:
        self.field = ft.TextField(
            expand=True,
            input_filter=self._get_input_filter(),
            on_change=self._on_field_changed,
        )

        options = self._dropdown_options()
        self.dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(o) for o in options],
            value=options[0],
            width=140,
            on_select=self._on_dropdown_selected,
        ) if len(options) > 1 else None

        controls = [self.field]
        if self.dropdown is not None:
            controls.append(self.dropdown)
        return ft.Row(controls, expand=True)


class FletTextEntry(FletEntry):
    """A row with a text field for string values."""
    valid_types: tuple[type, ...] = (*inc_optional(str),)


class FletFloatEntry(FletEntry):
    """A row with a float field."""
    valid_types: tuple[type, ...] = (*inc_optional(float),)

    def _get_input_filter(self) -> Optional[ft.InputFilter]:
        return ft.InputFilter(regex_string=r"^-?\d*\.?\d*$", allow=True)

    @property
    def cast_value(self) -> Optional[float]:
        try:
            return float(self.value) if self.value else None
        except (TypeError, ValueError):
            return None


class FletIntEntry(FletEntry):
    """A row with an integer field.

    NOTE: matches tkinter IntEntry's pre-existing quirk of not allowing a
    leading '-' for negative numbers, preserved here for parity.
    """
    valid_types: tuple[type, ...] = (*inc_optional(int),)

    def _get_input_filter(self) -> Optional[ft.InputFilter]:
        return ft.InputFilter(regex_string=r"^\d*$", allow=True)

    @property
    def cast_value(self) -> Optional[int]:
        try:
            return int(self.value) if self.value else None
        except (TypeError, ValueError):
            return None


class FletPathEntry(FletEntry):
    """A row with a plain text field for path values.

    NOTE: ft.FilePicker triggers "Unknown control: FilePicker" in the
    installed flet-desktop 0.86.1 client, confirmed via an isolated
    minimal repro independent of this codebase. Rather than fight that
    client bug, this is a plain text field for now — no Browse button.
    """
    valid_types: tuple[type, ...] = (*inc_optional(Path),)

    def __init__(self, allow_directory: bool = True, allow_file: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.allow_directory = allow_directory
        self.allow_file = allow_file

    @property
    def cast_value(self) -> Optional[Path]:
        try:
            return Path(self.value) if self.value else None
        except (TypeError, ValueError):
            return None
