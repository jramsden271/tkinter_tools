import inspect
from typing import Any, Callable, List, Optional, Union
from core.parameter_info import ParameterInfo


class MethodInfo:
    """Analyze a method or function signature for parameter metadata."""

    def __init__(self, method: Callable):
        self.method = method
        self.method_name = method.__name__
        self.signature = inspect.signature(method)
        self.parameters: List[ParameterInfo] = [
            ParameterInfo(parameter) for parameter in self.signature.parameters.values()
        ]
        self.accepts_varargs = any(p.is_var_positional for p in self.parameters)
        self.accepts_kwargs = any(p.is_var_keyword for p in self.parameters)
        self.return_annotation = (
            None
            if self.signature.return_annotation is inspect._empty
            else self.signature.return_annotation
        )
        self.docstring = inspect.getdoc(method)

    @property
    def parameter_names(self) -> List[str]:
        return [parameter.name for parameter in self.parameters]

    @property
    def required_parameters(self) -> List[ParameterInfo]:
        return [parameter for parameter in self.parameters if parameter.required]

    @property
    def optional_parameters(self) -> List[ParameterInfo]:
        return [parameter for parameter in self.parameters if not parameter.required]

    @property
    def formatted_title(self) -> str:
        """Return method name formatted as a readable title (underscores replaced with spaces, title-cased)."""
        return self.method_name.replace("_", " ").title()

    def get_help_text(self) -> str:
        """Return a user-facing help summary for this method."""
        lines = ["Parameters:"]

        required = self.required_parameters
        optional = self.optional_parameters

        if required:
            lines.append("  Required:")
            lines.extend(f"    {param.friendly_text()}" for param in required)
        if optional:
            lines.append("  Optional:")
            lines.extend(f"    {param.friendly_text()}" for param in optional)

        if self.accepts_varargs:
            lines.append("  This method accepts additional positional arguments.")
        if self.accepts_kwargs:
            lines.append("  This method accepts additional keyword arguments.")

        if self.return_annotation is not None:
            lines.append(f"Returns: {self.return_annotation}")

        return "\n".join(line for line in lines if line != "")
