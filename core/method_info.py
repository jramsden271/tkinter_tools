import inspect
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union
from core.parameter_info import ParameterInfo


@dataclass(frozen=True)
class HelpRow:
    """A single parameter's data for display in a help table."""
    name: str
    type_text: str
    default_text: str
    description: str


class MethodInfo:
    """Analyze a method or function signature for parameter metadata."""

    _PARAM_DESCRIPTION_PATTERN = r':param\s+(\w+):\s*(.+?)(?=\n\s*:|\n\n|$)'
    _FIELD_LINE_PATTERN = r'^\s*:\w+.*$'

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

    @property
    def summary(self) -> str:
        """Return the free-text summary from the docstring, excluding :param:/:type:/etc. field lines."""
        if not self.docstring:
            return ""

        first_field_match = re.search(self._FIELD_LINE_PATTERN, self.docstring, re.MULTILINE)
        summary_text = self.docstring[:first_field_match.start()] if first_field_match else self.docstring
        return summary_text.strip()

    @property
    def parameter_descriptions(self) -> Dict[str, str]:
        """Parse Sphinx-style :param name: descriptions from this method's docstring."""
        if not self.docstring:
            return {}

        matches = re.findall(self._PARAM_DESCRIPTION_PATTERN, self.docstring, re.DOTALL)
        return {name: desc.strip() for name, desc in matches}

    def help_rows(self) -> List[HelpRow]:
        """Return one HelpRow per parameter, for display in a help table."""
        descriptions = self.parameter_descriptions
        return [
            HelpRow(
                name=parameter.name,
                type_text=parameter.type_text,
                default_text=parameter.default_text,
                description=descriptions.get(parameter.name, ""),
            )
            for parameter in self.parameters
        ]

    def help_notes(self) -> List[str]:
        """Return supplementary help notes not tied to a specific parameter row."""
        notes = []
        if self.accepts_varargs:
            notes.append("This method accepts additional positional arguments.")
        if self.accepts_kwargs:
            notes.append("This method accepts additional keyword arguments.")
        if self.return_annotation is not None:
            notes.append(f"Returns: {self.return_annotation}")
        return notes

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
