import inspect
import re
from dataclasses import dataclass
from typing import Any, Callable, List, Optional


@dataclass(frozen=True)
class ParameterInfo:
    name: str
    annotation: Optional[Any]
    default: Optional[Any]
    kind: inspect._ParameterKind
    has_default: bool
    optional: bool
    is_var_positional: bool
    is_var_keyword: bool


class MethodSignature:
    """Analyze a method or function signature for parameter metadata."""

    def __init__(self, method: Callable):
        self.method = method
        self.method_name = method.__name__
        self.signature = inspect.signature(method)
        self.parameters: List[ParameterInfo] = [
            self._build_parameter_info(parameter)
            for parameter in self.signature.parameters.values()
        ]
        self.accepts_varargs = any(p.is_var_positional for p in self.parameters)
        self.accepts_kwargs = any(p.is_var_keyword for p in self.parameters)
        self.return_annotation = self._normalize_annotation(self.signature.return_annotation)
        self.docstring = inspect.getdoc(method)

    @staticmethod
    def _normalize_annotation(annotation: Any) -> Optional[Any]:
        return None if annotation is inspect._empty else annotation

    @staticmethod
    def _build_parameter_info(parameter: inspect.Parameter) -> ParameterInfo:
        annotation = MethodSignature._normalize_annotation(parameter.annotation)
        default = None if parameter.default is inspect._empty else parameter.default
        has_default = parameter.default is not inspect._empty
        is_var_positional = parameter.kind == inspect.Parameter.VAR_POSITIONAL
        is_var_keyword = parameter.kind == inspect.Parameter.VAR_KEYWORD
        optional = has_default or is_var_positional or is_var_keyword

        return ParameterInfo(
            name=parameter.name,
            annotation=annotation,
            default=default,
            kind=parameter.kind,
            has_default=has_default,
            optional=optional,
            is_var_positional=is_var_positional,
            is_var_keyword=is_var_keyword,
        )

    @property
    def parameter_names(self) -> List[str]:
        return [parameter.name for parameter in self.parameters]

    @property
    def required_parameters(self) -> List[ParameterInfo]:
        return [parameter for parameter in self.parameters if not parameter.optional]

    @property
    def optional_parameters(self) -> List[ParameterInfo]:
        return [parameter for parameter in self.parameters if parameter.optional]

    @property
    def formatted_title(self) -> str:
        """Return method name formatted as a readable title (underscores replaced with spaces, title-cased)."""
        return self.method_name.replace('_', ' ').title()
