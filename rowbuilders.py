import tkinter as tk
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, Optional, Callable
import regex
from pathlib import Path
from dataclasses import dataclass

T = TypeVar('T')

class Row(ABC):
    id:str
    kwargs:dict
    _label:str = "Unlabelled object" #all rowbuilders can take a label, up to children what to do with it

    #defaults
    _WIDTH:int = 30
    _PADX:int = 10
    _PADY:int = 2

    @abstractmethod
    def build(self, root:tk.Tk, row:int):
        pass

    def _default_padding(self, **kwargs) -> dict:
        return {
            "padx": kwargs.get("padx") or self._PADX,
            "pady": kwargs.get("pady") or self._PADY
        }
    
    @property
    def label(self) -> str:
        return self._label
    
    @label.setter
    def label(self, value:str):
        self._label = value
    
class ValueRow(Row, ABC, Generic[T]):
    """A rowbuilder with a value that can be get and set."""
    _value:Optional[T]

    @property
    @abstractmethod
    def value(self) -> T:
        pass

    @value.setter
    @abstractmethod
    def value(self, val:T):
        pass

    @abstractmethod
    def push_value(self):
        pass

    @abstractmethod
    def pull_value(self):
        pass

    @property
    @abstractmethod
    def cast_value(self) -> T:
        pass

class Text(Row):

    def __init__(self, label:str, id:str="", **kwargs):
        self.label = label
        self.id=id
        self.kwargs = kwargs

    def build(self, root:tk.Tk, row:int, **kwargs):
        self.kwargs = {**self.kwargs, **kwargs}
        self.label_obj = tk.Label(root, text=self.label)
        self.label_obj.grid(row=row, column=0, sticky="", columnspan=2, **self._default_padding(**self.kwargs))

class Entry(ValueRow, Generic[T]):
    entry_obj:Optional[tk.Entry] = None

    def __init__(self, id:str="", **kwargs):
        self.id=id
        self.kwargs = kwargs

    @property
    def cast_value(self) -> Optional[T]:
        return self.value if self.value else None #type:ignore

    @property
    def value(self) -> str|None:
        return self._value
    
    @value.setter
    def value(self, val:str):
        self._value = val

    def _get_validator(self) -> None|Callable:
        return None
    
    def push_value(self):
        if self.entry_obj and self.value:
            self.entry_obj.delete(0, tk.END)
            self.entry_obj.insert(0, str(self.value))

    def pull_value(self):
        if self.entry_obj:
            self.value = self.entry_obj.get()

    def build(self, root:tk.Tk, row:int):

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

class FloatEntry(Entry):

    def _get_validator(self):
        return lambda v: regex.fullmatch(r"-?\d*\.?\d*", v) is not None
    
    @property
    def cast_value(self) -> Optional[float]:
        try:
            return float(self.value) if self.value else None
        except:
            return None

class IntEntry(Entry):

    def _get_validator(self):
        return lambda v: not v or v.isdigit()
    
    @property
    def cast_value(self) -> int|None:
        try:
            return int(self.value) if self.value else None
        except:
            return None
    
class BoolEntry(Entry):

    def _get_validator(self) -> Callable:
        return lambda v: regex.fullmatch(r"[tfTF10]?", v) is not None
    
    @property
    def cast_value(self) -> Optional[bool]:
        if not self.value:
            return None
        if self.value.lower() in ["true", "t", "1"]:
            return True
        elif self.value.lower() in ["false", "f", "0"]:
            return False
        return None
    
class PathEntry(Entry):

    @property
    def cast_value(self) -> Optional[Path]:
        try:
            return Path(self.value) if self.value else None
        except:
            return None


