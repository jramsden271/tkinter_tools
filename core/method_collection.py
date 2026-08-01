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
        final_args, _overridden = self._collect_final_args_with_overrides(method)
        return final_args

    def _collect_final_args_with_overrides(self, method: MethodInfo) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Like collect_final_args, but also returns the subset of args the user overrode
        away from their default (used to summarize a queued call for display)."""
        final_args: Dict[str, Any] = {}
        overridden_args: Dict[str, Any] = {}
        accepted_names = {
            parameter.name
            for parameter in method.parameters
            if parameter.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
        }

        for parameter_state in self.parameter_states:
            if parameter_state.rowbuilder:
                parameter_state.rowbuilder.pull_value()
                if parameter_state.name in accepted_names or method.accepts_kwargs:
                    value = parameter_state.rowbuilder.cast_value
                    final_args[parameter_state.name] = value
                    if parameter_state.rowbuilder.is_overridden:
                        overridden_args[parameter_state.name] = value

        return final_args, overridden_args

    @staticmethod
    def format_params_summary(overridden_args: Dict[str, Any]) -> str:
        """Format the user-overridden args as a compact 'name=value, ...' string."""
        return ", ".join(f"{name}={value!r}" for name, value in overridden_args.items())

    def create_submit_action(self, method: MethodInfo) -> Callable[[], Any]:
        """Capture the current form values now and return a callable that invokes the
        method with that snapshot, so later widget edits don't affect a queued call."""
        final_args, _overridden = self._collect_final_args_with_overrides(method)

        def submit_action():
            return method.method(**final_args)

        return submit_action

    def create_submit_action_with_summary(self, method: MethodInfo) -> tuple[Callable[[], Any], str]:
        """Like create_submit_action, but also returns a compact summary of the
        overridden parameters for display in the Tasks window."""
        final_args, overridden_args = self._collect_final_args_with_overrides(method)

        def submit_action():
            return method.method(**final_args)

        return submit_action, self.format_params_summary(overridden_args)
