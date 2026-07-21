"""Flet-based row builders, mirroring the tkinter rowbuilders/ package.

Selection registry maps a parameter annotation to a Flet-facing builder
class, matching the same `valid_types` contract used by rowbuilders/.
"""

from .abstract import FletValueRow
from .entries import FletEntry, FletTextEntry, FletFloatEntry, FletIntEntry, FletPathEntry
from .widgets import FletCheckBox

FLET_VALUE_ROWBUILDERS = [FletTextEntry, FletFloatEntry, FletIntEntry, FletPathEntry, FletCheckBox]


def select_flet_rowbuilder(annotation):
    """Select the appropriate Flet row builder class based on the annotation."""
    matches = [r for r in FLET_VALUE_ROWBUILDERS if annotation in list(r.valid_types)]
    return matches[0] if matches else None
