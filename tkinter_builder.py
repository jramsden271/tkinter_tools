import tkinter as tk
from tkinter import messagebox
import inspect
from typing import Callable, Optional, Any
from pathlib import Path

from method_signature import MethodSignature
from rowbuilders import TextEntry, Text, ValueRow, IntEntry, FloatEntry, PathEntry, CheckBox
from styles import apply_style, get_button_style, COLORS, FONTS, SPACING

types_dict = {
    None: TextEntry,
    str: TextEntry,
    int: IntEntry,
    float: FloatEntry,
    Path: PathEntry,
    bool: CheckBox
}

class ParameterState:

    def __init__(self, value_type:Optional[Any], initial_value:Any, name:str, has_default:bool=False):
        self.name = name
        self.value_type = value_type
        self.initial_value = initial_value
        self.has_default = has_default
        self.rowbuilder:Optional[ValueRow] = None

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
    def _annotation_label(value_type:Optional[Any]) -> str:
        if value_type is None:
            return "Any"
        if isinstance(value_type, type):
            return value_type.__name__
        return str(value_type)

    @property
    def required(self) -> bool:
        return not self.has_default

    def build(self, root, row):
        if self.rowbuilder:
            required_ast = "*" if self.required else ""
            annotation_label = self._annotation_label(self.value_type)
            label_text = f"{self.name.replace('_', ' ').capitalize()} ({annotation_label}){required_ast}"
            
            self.rowbuilder.label = label_text
            
            if not self.required:
                self.rowbuilder.value = self.initial_value

            self.rowbuilder.build(root, row)


class TKinterInput:

    def __init__(self, methods:Callable|list[Callable], root:Optional[tk.Tk]=None, keep_on_top:bool=False, test_mode:bool=False, style:str="light"):
        self.parameter_states:list[ParameterState] = []
        methods = methods if isinstance(methods, list) else [methods]
        self.methods = [MethodSignature(method) for method in methods]
        self.style = style

        if root:
            self.root = root
        else:
            self.root = tk.Tk()

        for method in self.methods:
            for parameter_info in method.parameters:
                if parameter_info.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                    if parameter_info.name not in [parameter.name for parameter in self.parameter_states]:
                        self.parameter_states.append(ParameterState.from_parameter_info(parameter_info))

        row = 0

        self.root.title(self.methods[0].formatted_title)

        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

        # Apply modern styling before building widgets so labels, entries, and buttons inherit theme defaults.
        apply_style(self.root, style=self.style)

        doc_string = self.methods[0].docstring
        if doc_string:
            Text(doc_string).build(self.root, row)
            row += 1

        for para in self.parameter_states:
            if para.rowbuilder:
                para.rowbuilder.value = para.initial_value
                # Pass parameter description from parsed docstring
                para.build(self.root, row)
                row += 1

        for i in range(row): 
             self.root.grid_rowconfigure(i, weight=1)

        for method in self.methods:
             tk.Button(
                self.root,
                text=f"Run {method.formatted_title}",
                command=self._create_submit_action(method),
                **get_button_style(self.style)
             ).grid(row=row, column=0, columnspan=2, pady=SPACING["button_pady"], padx=SPACING["padding"], sticky="ew")
             row += 1

        if keep_on_top:
            self.root.attributes('-topmost', True)
            self.root.lift()

        if not test_mode:
            self.root.mainloop()
    
    def _create_submit_action(self, method: MethodSignature):
        """Create a submit action closure for the given method."""
        def submit_action():
            final_args = {}
            for para in self.parameter_states:
                if para.rowbuilder:
                    para.rowbuilder.pull_value()
                    final_args[para.name] = para.rowbuilder.cast_value

            try:
                method.method(**final_args)
            except TypeError as e:
                messagebox.showerror("Error", f"{e}")
        
        return submit_action

if __name__ == "__main__":

    def test_method_123(id: int, rate: float, name:str, some_path:Path, is_active:bool = False, another_default:int = 123, another:str = "asdf", floaty:float=1.23, *args123, **kwargs):
        """
        Docstring for test_method_123
        
        :param id: Description
        :type id: int
        :param rate: Description
        :type rate: float
        :param name: Description
        :param is_active: Description
        :type is_active: bool
        :param args123: Description
        :param kwargs: Description
        """
        print(f"ID Type: {id}, Rate Type: {rate}, Name Type: {name}, Active Type: {is_active}")

    def test_method_456(name:str, age:int=30, **kwargs):
        print(f"Name: {name}, Age: {age}")

    TKinterInput([test_method_123, test_method_456])