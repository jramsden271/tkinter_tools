import tkinter as tk
from tkinter import messagebox
import inspect
from typing import Type, Callable, Optional, Any
import regex
from pathlib import Path

from rowbuilders import Entry, Row, Text, ValueRow, IntEntry, FloatEntry, PathEntry, BoolEntry

types_dict = {
    inspect._empty: Entry,
    str: Entry,
    int: IntEntry, 
    float: FloatEntry, 
    Path: PathEntry, 
    bool: BoolEntry
}

class ParameterState:

    def __init__(self, value_type:Optional[Type], initial_value:Any, name:str, **kwargs):
        self.name = name
        self.value_type=value_type
        self.initial_value=initial_value
        self.kwargs = kwargs
        self.rowbuilder:Optional[ValueRow] = None

        if self.value_type in types_dict:
            self.rowbuilder = types_dict[self.value_type]()
        
    @classmethod
    def from_parameter(cls, parameter:inspect.Parameter):
        value = parameter.default
        if value == inspect._empty:
            value = None
        value_type = parameter.annotation
        if value_type == inspect._empty:
            value_type = None
        return cls(value_type, value, parameter.name)

    @property
    def required(self) -> bool:
        return self.value_type == inspect._empty

    def build(self, root, row):
        if self.rowbuilder:
            required_ast = "*" if self.required else ""
            self.rowbuilder.label = f"{self.name.replace('_', ' ').capitalize()} ({self.value_type}){required_ast}"
            
            if not self.required:
                self.rowbuilder.value = self.initial_value

            self.rowbuilder.build(root, row)


class TKinterInput:

    def __init__(self, method:Callable, root:Optional[tk.Tk]=None):
        self.parameter_states:list[ParameterState] = []
        self.method = method 
        if root:
            self.root = root
        else:
            self.root = tk.Tk()

        row = 0

        for parameter in inspect.signature(self.method).parameters.values():
            if parameter.kind == inspect._ParameterKind.POSITIONAL_OR_KEYWORD: #this ignores *args and **kwargs
                if parameter_state := ParameterState.from_parameter(parameter):
                    self.parameter_states.append(parameter_state)

        formatted_title = self.method.__name__.replace('_', ' ').title()
        self.root.title(formatted_title) 

        self.root.grid_columnconfigure(0, weight=0) 
        self.root.grid_columnconfigure(1, weight=1) 

        doc_string = self.method.__doc__
        if doc_string and len(doc_string) > 0:
            Text(doc_string).build(self.root, row)
            row += 1

        for para in self.parameter_states:
            if para.rowbuilder:
                para.rowbuilder.value = para.initial_value
                para.build(self.root, row)
                row += 1

        for i in range(row): 
             self.root.grid_rowconfigure(i, weight=1)

        submit_button = tk.Button(
            self.root,
            text="Submit",
            command=self.submit_action 
        )
        submit_button.grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        self.root.mainloop()
    
    def submit_action(self) -> None:
        final_args = {}
        for para in self.parameter_states:
            if para.rowbuilder:
                para.rowbuilder.pull_value()
                #final_args[para.name] = TKinterInput.cast(para.row.value, para.type)
                final_args[para.name] = para.rowbuilder.cast_value

        print(f"Submitting data (with types) to {self.method.__name__}: {final_args}")
        try:
            self.method(**final_args)
        except TypeError as e:
            messagebox.showerror("Error", f"{e}")

if __name__ == "__main__":

    def test_method_123(id: int, rate: float, name, some_path:Path, is_active:bool = False, another_default:int = 123, another:str = "asdf", floaty:float=1.23, *args123, **kwargs):
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

    TKinterInput(test_method_123)