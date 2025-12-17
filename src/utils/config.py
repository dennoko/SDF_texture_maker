import os
import sys

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Font Configuration
FONT_FAMILIES = [
    "Yu Gothic UI",      # Windows 10/11
    "Meiryo UI",         # Windows 7/8
    "MS UI Gothic",      # Old Windows
    "Segoe UI",          # English
    "Arial",             # Fallback
    "sans-serif"         # Fallback
]

# UI Configuration
WINDOW_TITLE = "SDF Make Supporter for lilToon"
WINDOW_GEOMETRY = "1200x800"
THEME_MODE = "dark"
THEME_COLOR = "dark-blue"

# File Types
IMAGE_FILE_TYPES = [("画像ファイル", "*.png *.jpg *.jpeg *.bmp *.tiff *.tga")]
PNG_FILE_TYPE = [("PNG画像", "*.png")]
