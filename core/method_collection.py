import inspect
from typing import Any, Callable, Dict, List, Optional

from .method_info import MethodInfo
from .parameter_state import ParameterState


class MethodCollection:
    """Encapsulate method metadata and shared form parameter handling."""

    def __init__(self, methods: Callable | list[Callable]):
        self.methods = self._normalize_methods(methods)
        self.parameter_states = self._build_parameter_states()

    @staticmethod
    def _normalize_methods(methods: Callable | list[Callable]) -> List[MethodInfo]:
        if isinstance(methods, list):
            return [MethodInfo(method) for method in methods]
        return [MethodInfo(methods)]

    def _build_parameter_states(self) -> List[ParameterState]:
        unique_names = set()
        states: List[ParameterState] = []

        for method in self.methods:
            for parameter_info in method.parameters:
                if parameter_info.kind != inspect.Parameter.POSITIONAL_OR_KEYWORD:
                    continue
                if parameter_info.name in unique_names:
                    continue

                unique_names.add(parameter_info.name)
                states.append(ParameterState.from_parameter_info(parameter_info))

        return states

    @property
    def title(self) -> str:
        return self.methods[0].formatted_title if self.methods else ""

    @property
    def docstring(self) -> Optional[str]:
        return self.methods[0].docstring if self.methods else None

    @property
    def parameter_descriptions(self) -> Dict[str, str]:
        """Collect parameter descriptions from the first method's docstring."""
        if not self.methods:
            return {}

        return self.methods[0].parameter_descriptions

    def get_parameter_description(self, param_name: str) -> Optional[str]:
        """Get the description for a specific shared parameter."""
        return self.parameter_descriptions.get(param_name)

    def collect_final_args(self, method: MethodInfo) -> Dict[str, Any]:
        """Collect values from shared parameter states and filter them for the target method."""
        final_args: Dict[str, Any] = {}
        accepted_names = {
            parameter.name
            for parameter in method.parameters
            if parameter.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
        }

        for parameter_state in self.parameter_states:
            if parameter_state.rowbuilder:
                parameter_state.rowbuilder.pull_value()
                if parameter_state.name in accepted_names or method.accepts_kwargs:
                    final_args[parameter_state.name] = parameter_state.rowbuilder.cast_value

        return final_args

    def create_submit_action(self, method: MethodInfo) -> Callable[[], Any]:
        """Capture the current form values now and return a callable that invokes the
        method with that snapshot, so later widget edits don't affect a queued call."""
        final_args = self.collect_final_args(method)

        def submit_action():
            return method.method(**final_args)

        return submit_action
