"""
Dark theme implementation - modern dark appearance suitable for low-light environments.
"""

from typing import Dict, Any, Tuple
from .custom import CustomStyle


class DarkStyle(CustomStyle):
    """Modern dark theme with dark backgrounds and light text."""
    
    @property
    def colors(self) -> Dict[str, str]:
        """Dark theme color palette."""
        return {
            "bg_primary": "#1e1e1e",       # Dark background
            "bg_secondary": "#2d2d2d",     # Slightly lighter background for content
            "text_primary": "#e0e0e0",     # Light gray for text
            "text_secondary": "#9e9e9e",   # Medium gray for secondary text
            "accent": "#2196f3",           # Lighter blue for dark theme
            "accent_dark": "#1976d2",      # Darker blue for hover
            "border": "#424242",           # Dark border
            "error": "#f44336",            # Red for errors
            "success": "#66bb6a",          # Green for success
            "button_fg": "#1e1e1e",        # Dark text for buttons
            "button_active_fg": "#1e1e1e", # Dark text for active buttons
        }
