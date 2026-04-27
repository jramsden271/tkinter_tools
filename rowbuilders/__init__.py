"""Row builders for tkinter applications.

This package provides a collection of row builder classes for constructing
structured forms in tkinter applications.

Classes are organized into:
- Abstract bases: Row, ValueRow
- Simple widgets: Text
- Entry-based: Entry, FloatEntry, IntEntry, PathEntry
- Specialized widgets: CheckBox, BoolEntry
"""

from typing import Union

from .abstract import Row, ValueRow
from .simple import Text
from rowbuilders.entries import Entry, TextEntry, FloatEntry, IntEntry, PathEntry
from .widgets import CheckBox
from pathlib import Path

VALUE_ROWBUILDERS = [TextEntry, FloatEntry, IntEntry, PathEntry, CheckBox]

def select_rowbuilder(annotation):
    """Select the appropriate row builder class based on the annotation."""

    rowbuilders = [r for r in VALUE_ROWBUILDERS if annotation in list(r.valid_types)]
    if any(rowbuilders):
        return rowbuilders[0]
    
