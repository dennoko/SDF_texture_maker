import customtkinter as ctk
from typing import TYPE_CHECKING, Dict, Any
from tkinter import filedialog
import os

if TYPE_CHECKING:
    from ..app import SDFTextureApp

class ChannelPanel(ctk.CTkFrame):
    """Panel for B/A Channel configuration (Collapsible)"""
    
    def __init__(self, parent, app: "SDFTextureApp", **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.ui_elements: Dict[str, Any] = {}
        self.is_expanded = ctk.BooleanVar(value=False)
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Toggle Button (Header)
        self.ui_elements['btn_toggle'] = ctk.CTkCheckBox(
            self, 
            text="", 
            variable=self.is_expanded,
            command=self._toggle_content,
            font=self.app.font_normal,
            width=20, # Small check box
        )
        self.ui_elements['btn_toggle'].pack(anchor="w", padx=10, pady=(5, 5))
        
        # Content Frame (Initially hidden)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        # Don't pack initially (collapsed state)
        
        # B Channel
        self._create_channel_group('B')
        
        # A Channel
        self._create_channel_group('A')
        
    def _toggle_content(self):
        """Toggle visibility of content frame"""
        if self.is_expanded.get():
            self.content_frame.pack(fill="x", padx=5, pady=5)
        else:
            self.content_frame.pack_forget()

    def _create_channel_group(self, channel_type: str):
        """Create UI group for a channel (Vertical Layout)"""
        # Outer container for the group
        group_frame = ctk.CTkFrame(self.content_frame)
        group_frame.pack(fill="x", padx=0, pady=5)
        
        # Row 1: Label
        lbl_key = f'lbl_channel_{channel_type.lower()}'
        self.ui_elements[lbl_key] = ctk.CTkLabel(
            group_frame, 
            text=f"{channel_type} Channel:", 
            font=self.app.font_body,
            anchor="w"
        )
        self.ui_elements[lbl_key].pack(fill="x", padx=5, pady=(5, 0))
        
        # Row 2: Entry + Buttons
        input_frame = ctk.CTkFrame(group_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=0, pady=(2, 5))
        
        # Path Entry
        path_var = self.app.b_channel_path if channel_type == 'B' else self.app.a_channel_path
        entry = ctk.CTkEntry(input_frame, textvariable=path_var, font=self.app.font_body, height=28)
        entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Browse Button
        btn_browse_key = f'btn_browse_{channel_type.lower()}'
        cmd_browse = lambda: self.app.browse_extra_channel(channel_type)
        self.ui_elements[btn_browse_key] = ctk.CTkButton(
            input_frame, text="...", width=30, height=28, font=self.app.font_body, command=cmd_browse
        )
        self.ui_elements[btn_browse_key].pack(side="left", padx=2)

        # Clear Button
        btn_clear_key = f'btn_clear_{channel_type.lower()}'
        cmd_clear = lambda: self.app.clear_extra_channel(channel_type)
        self.ui_elements[btn_clear_key] = ctk.CTkButton(
            input_frame, text="x", width=30, height=28, fg_color="#555555", hover_color="#777777",
            font=self.app.font_body, command=cmd_clear
        )
        self.ui_elements[btn_clear_key].pack(side="left", padx=(2, 5))

    def update_texts(self):
        """Update localized texts"""
        lang = self.app.lang
        self.ui_elements['btn_toggle'].configure(text=lang.get("lbl_advanced_options"))
