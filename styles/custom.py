"""
CustomStyle base class providing common styling elements for themes.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from . import Style
import ctypes


class CustomStyle(Style):
    """Base class for custom themes with common styling elements."""
    
    @property
    @abstractmethod
    def colors(self) -> Dict[str, str]:
        """Return color palette dictionary - must be implemented by subclasses."""
        pass
    
    @property
    def fonts(self) -> Dict[str, Tuple]:
        """Common typography configuration."""
        return {
            "label": ("Segoe UI", 12),
            "label_bold": ("Segoe UI", 12, "bold"),
            "title": ("Segoe UI", 14, "bold"),
            "entry": ("Segoe UI", 12),
            "button": ("Segoe UI", 12, "bold"),
            "docstring": ("Segoe UI", 10),
        }
    
    @property
    def spacing(self) -> Dict[str, int]:
        """Common spacing and layout configuration."""
        return {
            "padding": 10,
            "button_pady": 8,
            "label_width": 20,
        }
    
    @property
    def button_config(self) -> Dict[str, Any]:
        """Button styling using theme colors."""
        colors = self.colors
        return {
            "bg": colors["accent"],
            "fg": colors.get("button_fg", "#ffffff"),
            "activebackground": colors["accent_dark"],
            "activeforeground": colors.get("button_active_fg", "#ffffff"),
            "relief": "flat",
            "cursor": "hand2",
            "bd": 0,
        }
    
    @property
    def entry_config(self) -> Dict[str, Any]:
        """Entry widget styling using theme colors."""
        colors = self.colors
        return {
            "bg": colors["bg_secondary"],
            "fg": colors["text_primary"],
            "relief": "solid",
            "bd": 1,
            "insertbackground": colors["accent"],
        }
    
    @property
    def label_config(self) -> Dict[str, Any]:
        """Label styling using theme colors."""
        colors = self.colors
        return {
            "bg": colors["bg_primary"],
            "fg": colors["text_primary"],
            "font": self.fonts["label"],
        }
    
    def apply_to_window(self, root):
        """Apply common theme styling to a tkinter root window."""
        colors = self.colors
        spacing = self.spacing
        
        # Configure main window background
        root.configure(bg=colors["bg_primary"])

        # Apply default widget appearance for the theme
        root.option_add("*Label.background", colors["bg_primary"])
        root.option_add("*Label.foreground", colors["text_primary"])
        root.option_add("*Label.font", self.fonts["label"])
        root.option_add("*Entry.background", colors["bg_secondary"])
        root.option_add("*Entry.foreground", colors["text_primary"])
        root.option_add("*Entry.font", self.fonts["entry"])
        root.option_add("*Entry.insertBackground", colors["accent"])
        root.option_add("*Entry.relief", "solid")
        root.option_add("*Entry.borderWidth", 1)
        root.option_add("*Button.background", colors["accent"])
        root.option_add("*Button.foreground", colors.get("button_fg", "#ffffff"))
        root.option_add("*Button.font", self.fonts["button"])
        root.option_add("*Button.activeBackground", colors["accent_dark"])
        root.option_add("*Button.activeForeground", colors.get("button_active_fg", "#ffffff"))
        root.option_add("*Button.relief", "flat")
        root.option_add("*Button.cursor", "hand2")
        root.option_add("*Button.borderWidth", 0)
        root.option_add("*Checkbutton.background", colors["bg_primary"])
        root.option_add("*Checkbutton.foreground", colors["text_primary"])
        root.option_add("*Checkbutton.font", self.fonts["label"])
        root.option_add("*Frame.background", colors["bg_primary"])
        root.option_add("*Canvas.background", colors["bg_primary"])
        
        # Set minimum window size
        root.minsize(400, 100)
        
        # Configure window appearance
        try:
            root.tk.call("tk", "scaling", 1.0)
        except:
            pass