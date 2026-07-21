"""Shared contract for Flet row builders."""
from typing import Any, Optional, Protocol, Union, runtime_checkable

import flet as ft


def inc_optional(annotation):
    """Include NoneType in the valid types if the annotation allows None."""
    return [annotation, Union[annotation, None], annotation | None]


@runtime_checkable
class FletValueRow(Protocol):
    """The contract MethodCollection.collect_final_args() needs: pull_value() then cast_value."""

    valid_types: tuple[type, ...]

    def build(self, label_width: Optional[int] = None) -> ft.Control:
        """Build and return the Flet control(s) for this row."""
        ...

    def pull_value(self) -> None:
        """Pull the value from the Flet control(s) into memory."""
        ...

    @property
    def cast_value(self) -> Any:
        """Get the value cast to the appropriate type."""
        ...
