import tkinter as tk
from typing import Callable, Optional, Any
from core.method_collection import MethodCollection
from rowbuilders import Text
from pathlib import Path
from styles import apply_style, get_button_style, COLORS, FONTS, SPACING
from help_window import HelpWindow



class TKinterInput:

    def __init__(self, methods:Callable|list[Callable], root:Optional[tk.Tk]=None, keep_on_top:bool=False, test_mode:bool=False, style:str="light"):
        self.method_collection = MethodCollection(methods)
        self.style = style

        if root:
            self.root = root
        else:
            self.root = tk.Tk()

        row = 0

        self.root.title(self.method_collection.title)

        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

        # Apply modern styling before building widgets so labels, entries, and buttons inherit theme defaults.
        apply_style(self.root, style=self.style)

        if doc_string := self.method_collection.docstring:
            Text(doc_string).build(self.root, row)
            row += 1

        for para in self.method_collection.parameter_states:
            if para.rowbuilder:
                para.rowbuilder.value = para.initial_value
                description = self.method_collection.get_parameter_description(para.name)
                para.build(self.root, row, param_description=description)
                row += 1

        for i in range(row): 
             self.root.grid_rowconfigure(i, weight=1)

        for method in self.method_collection.methods:
            row_frame = tk.Frame(self.root, bg=self.root.cget("bg"))
            row_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=SPACING["button_pady"], padx=SPACING["padding"])
            row_frame.columnconfigure(0, weight=1)

            tk.Button(
                row_frame,
                text=f"{method.formatted_title}",
                command=self.method_collection.create_submit_action(method),
                #**get_button_style(self.style)
            ).grid(row=0, column=0, sticky="ew")

            tk.Button(
                row_frame,
                text="Help",
                command=lambda m=method: HelpWindow(
                    self.root, 
                    f"Help: {m.formatted_title}",
                    m.get_help_text(),
                    self.style
                ),
                **get_button_style(self.style)
            ).grid(row=0, column=1, padx=(5, 0))

            row += 1

        if keep_on_top:
            self.root.attributes('-topmost', True)

        if not test_mode:
            self.root.mainloop()

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
        print(f"ID: {id}, Rate: {rate}, Name: {name}, Path: {some_path}, Active: {is_active}, Another Default: {another_default}, Another: {another}, Floaty: {floaty}")    

    def test_method_456(name:str|None, age:int=30):
        print(f"Name: {name}, Age: {age}")

    TKinterInput([test_method_123, test_method_456], style="light")