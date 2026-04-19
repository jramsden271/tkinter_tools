"""
Style theming system for TKinterInput windows.
Provides base style class and theme implementations (light, dark).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple


class Style(ABC):
    """
    Abstract base class for UI themes.
    Subclasses define specific color schemes, fonts, and spacing.
    """
    
    @property
    @abstractmethod
    def colors(self) -> Dict[str, str]:
        """Return color palette dictionary."""
        pass
    
    @property
    @abstractmethod
    def fonts(self) -> Dict[str, Tuple]:
        """Return fonts dictionary."""
        pass
    
    @property
    @abstractmethod
    def spacing(self) -> Dict[str, int]:
        """Return spacing/layout dictionary."""
        pass
    
    @property
    @abstractmethod
    def button_config(self) -> Dict[str, Any]:
        """Return button styling configuration."""
        pass
    
    @property
    @abstractmethod
    def entry_config(self) -> Dict[str, Any]:
        """Return entry widget styling configuration."""
        pass
    
    @property
    @abstractmethod
    def label_config(self) -> Dict[str, Any]:
        """Return label styling configuration."""
        pass
    
    @abstractmethod
    def apply_to_window(self, root):
        """Apply theme styling to a tkinter root window."""
        pass


from .custom import CustomStyle
from .light import LightStyle
from .dark import DarkStyle


def apply_style(root, style:str = "light"):
    """
    Apply the specified styling to a tkinter root window.
    
    Args:
        root: The tkinter Tk() window to style
        style: The style to apply ("light" or "dark")
    """

    # apply style according to style selection
    if style == "dark":
        from .dark import DarkStyle
        theme = DarkStyle()
        theme.apply_to_window(root)
    else:
        from .light import LightStyle
        theme = LightStyle()
        theme.apply_to_window(root)


def get_button_style(style: str = "light") -> Dict[str, Any]:
    """Get button styling configuration from the specified theme."""
    if style == "dark":
        from .dark import DarkStyle
        return DarkStyle().button_config.copy()
    from .light import LightStyle
    return LightStyle().button_config.copy()


def get_label_style(style: str = "light") -> Dict[str, Any]:
    """Get label styling configuration from the specified theme."""
    if style == "dark":
        from .dark import DarkStyle
        return DarkStyle().label_config.copy()
    from .light import LightStyle
    return LightStyle().label_config.copy()


def get_entry_style(style: str = "light") -> Dict[str, Any]:
    """Get entry styling configuration from the specified theme."""
    if style == "dark":
        from .dark import DarkStyle
        return DarkStyle().entry_config.copy()
    from .light import LightStyle
    return LightStyle().entry_config.copy()


# Color constants exported for convenience
from .light import LightStyle
_default_theme = LightStyle()
COLORS = _default_theme.colors.copy()
FONTS = _default_theme.fonts.copy()
SPACING = _default_theme.spacing.copy()


__all__ = [
    'Style',
    'CustomStyle',
    'LightStyle',
    'DarkStyle',
    'apply_style',
    'get_button_style',
    'get_label_style',
    'get_entry_style',
]
