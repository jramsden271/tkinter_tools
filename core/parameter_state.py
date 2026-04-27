from typing import Any, Optional, Union

from dataclasses import dataclass
from rowbuilders import TextEntry, IntEntry, FloatEntry, PathEntry, CheckBox, ValueRow
from pathlib import Path
from enum import Enum
from core.parameter_info import ParameterInfo
import rowbuilders
import tkinter as tk




from typing import Generic, TypeVar

T = TypeVar('T')

class ValueType(Enum):
    UNSET = 0
    NONE = 1
    DEFAULT = 2
    USER = 3

@dataclass
class ParameterState():
    name: str
    annotation: Any
    required: bool = True
    has_default: bool = False
    default_value: Any | None = None

    def __post_init__(self):
        builder_class = rowbuilders.select_rowbuilder(self.annotation)
        if builder_class:
            self.rowbuilder = builder_class(can_be_none=self.can_be_none, has_default=self.has_default, default=self.default_value)



    @classmethod
    def from_parameter_info(cls, parameter_info: ParameterInfo):
        return cls(
            parameter_info.name,
            parameter_info.annotation,
            parameter_info.required,
            parameter_info.has_default,
            parameter_info.default
        )
    
    def set_default(self, default_value: Any):
        self.default_value = default_value
        self.has_default = True

    @property
    def can_be_none(self) -> bool:
        if self.annotation in [None, type(None)]:
            return True
        if hasattr(self.annotation, "__origin__") and self.annotation.__origin__ is Union:
            return type(None) in self.annotation.__args__
        return False

    @staticmethod
    def _annotation_label(annotation: Any | None) -> str:
        if annotation is None:
            return "Any"
        if isinstance(annotation, type):
            return annotation.__name__
        return str(annotation)

    def build(self, root: tk.Tk, row: int, param_description: Optional[str] = None):
        if self.rowbuilder:
            annotation_label = self._annotation_label(self.annotation)
            label_text = f"{self.name.replace('_', ' ').capitalize()} ({annotation_label})"

            if param_description:
                label_text = f"{label_text}\n{param_description}"

            self.rowbuilder.label = label_text

            self.rowbuilder.build(root, row)
