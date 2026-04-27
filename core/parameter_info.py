import inspect
from types import NoneType
from typing import Any, Callable, List, Optional, Union
from attr import dataclass


@dataclass(frozen=True)
class ParameterInfo():
    parameter:inspect.Parameter

    @property
    def name(self) -> str:
        """Return the name of the parameter."""
        return self.parameter.name
    
    @property
    def kind(self) -> inspect._ParameterKind:
        """Return the kind of the parameter (positional, keyword, varargs, etc.)."""
        return self.parameter.kind

    @property
    def has_annotation(self) -> bool:
        """Check if the parameter has an annotation."""
        return self.annotation is not inspect._empty
    
    @property
    def annotation(self) -> Optional[Any]:
        """Return the annotation of the parameter, or None if there is no annotation."""
        return None if self.parameter.annotation is inspect._empty else self.parameter.annotation

    @property
    def union_annotation(self) -> Optional[List[Any]]:
        """Parse the annotation if the annotation is a Union, returns None otherwise."""
        if self.annotation and getattr(self.annotation, "__origin__", None) is Union:
            return self.parameter.annotation.__args__
        return None
    
    @property
    def can_be_none(self) -> bool:
        """Determine if the parameter can be None based on its annotation."""
        if self.annotation in [NoneType, inspect._empty]:
            return True
        if self.union_annotation:
            return type(None) in self.union_annotation
        return False
    
    @property
    def has_default(self) -> bool:
        """Check if the parameter has a default value."""
        return self.parameter.default is not inspect._empty
    
    @property
    def default(self) -> Optional[Any]:
        """Return the default value of the parameter, or None if there is no default."""
        return None if self.parameter.default is inspect._empty else self.parameter.default
    
    @property
    def required(self) -> bool:
        """Check if the parameter is required."""
        return (self.default is None) and (self.kind not in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD])

    @property
    def is_var_positional(self) -> bool:
        """Check if the parameter is a variable positional parameter (*args)."""
        return self.kind == inspect.Parameter.VAR_POSITIONAL
    
    @property
    def is_var_keyword(self) -> bool:
        """Check if the parameter is a variable keyword parameter (**kwargs)."""
        return self.kind == inspect.Parameter.VAR_KEYWORD
    
    def friendly_text(self) -> str:
        """Return a user-friendly string representation of the parameter."""
        annotation_text = self.annotation if self.annotation is not None else 'Any'
        default_text = f" = {self.default!r}" if self.has_default else ""
        kind_text = ""
        if self.is_var_positional:
            kind_text = " (varargs)"
        elif self.is_var_keyword:
            kind_text = " (kwargs)"
        return f"{self.name}: {annotation_text}{default_text}{kind_text}"