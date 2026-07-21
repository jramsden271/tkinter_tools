"""Abstract base classes for row builders."""
import tkinter as tk
from abc import ABC, abstractmethod
from types import NoneType
from typing import TypeVar, Generic, Optional, Union

T = TypeVar('T')

def inc_optional(annotation):
    """Include NoneType in the valid types if the annotation allows None."""
    return [annotation, Union[annotation, None], annotation | None]


class Row(ABC):
    """Abstract base class for all row builders."""
    id: str
    kwargs: dict
    _label: str = "Unlabelled object"  # all rowbuilders can take a label, up to children what to do with it

    # defaults
    _WIDTH: int = 30
    _PADX: int = 10
    _PADY: int = 2

    @abstractmethod
    def build(self, root: tk.Tk, label_width: Optional[int] = None, **kwargs) -> tk.Frame:
        """Build the row widgets into a frame and return it."""
        pass

    def _default_padding(self, **kwargs) -> dict:
        """Get default padding values from kwargs or use class defaults."""
        return {
            "padx": kwargs.get("padx") or self._PADX,
            "pady": kwargs.get("pady") or self._PADY
        }

    @property
    def label(self) -> str:
        """Get the label for this row."""
        return self._label

    @label.setter
    def label(self, value: str):
        """Set the label for this row."""
        self._label = value


class ValueRow(Row, ABC, Generic[T]):
    """A rowbuilder with a value that can be get and set."""
    _value: T
    _is_value_set: bool = False
    valid_types: tuple[type, ...] = ()  # to be defined in subclasses

    @property
    @abstractmethod
    def value(self) -> T:
        """Get the current value."""
        pass

    @value.setter
    @abstractmethod
    def value(self, val: T):
        """Set the value."""
        pass

    @abstractmethod
    def push_value(self):
        """Push the current value to the UI widget."""
        pass

    @abstractmethod
    def pull_value(self):
        """Pull the value from the UI widget."""
        pass

    @property
    @abstractmethod
    def cast_value(self) -> T:
        """Get the value cast to the appropriate type."""
        pass

    # @abstractmethod
    # def reset(self):
    #     """Reset the value to its default state."""
    #     pass
