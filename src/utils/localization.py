import json
import os
import locale
from typing import Dict, Any, Optional

from . import config

class LanguageManager:
    """Manages string resources and language settings"""
    
    def __init__(self, resource_path: str):
        self.strings: Dict[str, Dict[str, str]] = {}
        self.current_lang = "ja"  # Default
        self.load_strings(resource_path)
        self.load_settings()
        
    def load_strings(self, path: str):
        """Load strings from JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.strings = json.load(f)
        except Exception as e:
            print(f"Failed to load strings: {e}")
            self.strings = {}

    def get(self, key: str, *args) -> str:
        """Get string by key in current language"""
        if key not in self.strings:
            return key
        
        lang_dict = self.strings[key]
        text = lang_dict.get(self.current_lang, lang_dict.get("ja", key))
        
        if args:
            try:
                return text.format(*args)
            except Exception:
                return text
        return text

    def set_language(self, lang: str):
        """Set current language (ja/en)"""
        self.current_lang = lang
        self.save_settings()

    def load_settings(self):
        """Load language preference from settings.json"""
        settings_path = "settings.json"
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_lang = settings.get("language", "ja")
            except Exception:
                pass

    def save_settings(self):
        """Save language preference to settings.json"""
        settings_path = "settings.json"
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump({"language": self.current_lang}, f, indent=4)
        except Exception:
            pass
