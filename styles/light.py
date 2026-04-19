"""
Light theme implementation - modern, clean appearance with light backgrounds.
"""

from typing import Dict, Any, Tuple
from .custom import CustomStyle


class LightStyle(CustomStyle):
    """Modern light theme with light backgrounds and blue accents."""
    
    @property
    def colors(self) -> Dict[str, str]:
        """Light theme color palette."""
        return {
            "bg_primary": "#f5f5f5",       # Light gray background
            "bg_secondary": "#ffffff",     # White for content areas
            "text_primary": "#212121",     # Dark gray for text
            "text_secondary": "#757575",   # Medium gray for secondary text
            "accent": "#1976d2",           # Blue accent
            "accent_dark": "#1565c0",      # Darker blue for hover
            "border": "#e0e0e0",           # Light border
            "error": "#d32f2f",            # Red for errors
            "success": "#388e3c",          # Green for success
        }
