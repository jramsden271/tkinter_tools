from typing import Any, Optional
from rowbuilders import TextEntry, IntEntry, FloatEntry, PathEntry, CheckBox, ValueRow
from pathlib import Path

types_dict = {
    None: TextEntry,
    str: TextEntry,
    int: IntEntry,
    float: FloatEntry,
    Path: PathEntry,
    bool: CheckBox
}

class ParameterState:

    def __init__(self, value_type:Any|None, initial_value:Any, name:str, has_default:bool=False):
        self.name = name
        self.value_type = value_type
        self.initial_value = initial_value
        self.has_default = has_default
        self.rowbuilder:ValueRow|None = None

        if self.value_type in types_dict:
            self.rowbuilder = types_dict[self.value_type]()

    @classmethod
    def from_parameter_info(cls, parameter_info):
        return cls(
            value_type=parameter_info.annotation,
            initial_value=parameter_info.default,
            name=parameter_info.name,
            has_default=parameter_info.has_default,
        )

    @staticmethod
    def _annotation_label(value_type:Any|None) -> str:
        if value_type is None:
            return "Any"
        if isinstance(value_type, type):
            return value_type.__name__
        return str(value_type)

    @property
    def required(self) -> bool:
        return not self.has_default

    def build(self, root, row, param_description: Optional[str] = None):
        if self.rowbuilder:
            required_ast = "*" if self.required else ""
            annotation_label = self._annotation_label(self.value_type)
            label_text = f"{self.name.replace('_', ' ').capitalize()} ({annotation_label}){required_ast}"

            if param_description:
                label_text = f"{label_text}\n{param_description}"

            self.rowbuilder.label = label_text

            if not self.required:
                self.rowbuilder.value = self.initial_value

            self.rowbuilder.build(root, row)