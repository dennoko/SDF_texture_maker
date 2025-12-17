import customtkinter as ctk
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from ..app import SDFTextureApp

class ControlPanel(ctk.CTkFrame):
    """Left side control panel container"""
    
    def __init__(self, parent, app: "SDFTextureApp", **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.ui_elements: Dict[str, Any] = {}
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Title
        self.ui_elements['title'] = ctk.CTkLabel(self, text="", font=self.app.font_large)
        self.ui_elements['title'].pack(pady=(10, 20))
        
        # Input Section
        input_section = ctk.CTkFrame(self)
        input_section.pack(fill="x", padx=10, pady=5)
        
        self.ui_elements['lbl_gradient'] = ctk.CTkLabel(input_section, text="", font=self.app.font_normal)
        self.ui_elements['lbl_gradient'].pack(anchor="w", padx=10, pady=(10, 5))
        
        input_frame = ctk.CTkFrame(input_section)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.gradient_entry = ctk.CTkEntry(input_frame, textvariable=self.app.gradient_path)
        self.gradient_entry.pack(side="left", fill="x", expand=True, padx=(5, 5), pady=5)
        
        self.ui_elements['btn_browse_in'] = ctk.CTkButton(input_frame, text="", width=60, font=self.app.font_body,
                     command=self.app.browse_gradient)
        self.ui_elements['btn_browse_in'].pack(side="right", padx=(0, 5), pady=5)
        
        # Output Section
        output_section = ctk.CTkFrame(self)
        output_section.pack(fill="x", padx=10, pady=5)
        
        self.ui_elements['lbl_output_settings'] = ctk.CTkLabel(output_section, text="", font=self.app.font_normal)
        self.ui_elements['lbl_output_settings'].pack(anchor="w", padx=10, pady=(10, 5))
        
        # Checkboxes
        self.ui_elements['chk_auto_update'] = ctk.CTkCheckBox(
            output_section, text="", variable=self.app.auto_update, font=self.app.font_body, 
            command=self.app.toggle_auto_update)
        self.ui_elements['chk_auto_update'].pack(anchor="w", padx=10, pady=5)
        
        self.ui_elements['chk_overwrite'] = ctk.CTkCheckBox(
            output_section, text="", variable=self.app.overwrite_files, font=self.app.font_body)
        self.ui_elements['chk_overwrite'].pack(anchor="w", padx=10, pady=5)
        
        self.ui_elements['chk_channel_preview'] = ctk.CTkCheckBox(
            output_section, text="", variable=self.app.show_channel_preview, font=self.app.font_body, 
            command=self.app.toggle_channel_preview)
        self.ui_elements['chk_channel_preview'].pack(anchor="w", padx=10, pady=5)
        
        # Output Path
        output_frame = ctk.CTkFrame(output_section)
        output_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.ui_elements['lbl_output_path'] = ctk.CTkLabel(output_frame, text="", font=self.app.font_body)
        self.ui_elements['lbl_output_path'].pack(anchor="w", padx=5, pady=(5, 0))
        
        path_frame = ctk.CTkFrame(output_frame)
        path_frame.pack(fill="x", padx=5, pady=5)
        
        self.output_entry = ctk.CTkEntry(path_frame, textvariable=self.app.output_path)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(5, 5), pady=5)
        
        self.ui_elements['btn_browse_out'] = ctk.CTkButton(path_frame, text="", width=60, font=self.app.font_body,
                     command=self.app.browse_output)
        self.ui_elements['btn_browse_out'].pack(side="right", padx=(0, 5), pady=5)
        
        # Buttons
        self.ui_elements['btn_save'] = ctk.CTkButton(self, text="", height=35, font=self.app.font_body,
                     command=self.app.save_result)
        self.ui_elements['btn_save'].pack(fill="x", padx=10, pady=(10, 5))
        
        self.ui_elements['btn_save_as'] = ctk.CTkButton(self, text="", height=35, font=self.app.font_body,
                     command=self.app.save_as_result)
        self.ui_elements['btn_save_as'].pack(fill="x", padx=10, pady=(5, 20))
        
        # Language Switcher
        self.ui_elements['chk_english_mode'] = ctk.CTkCheckBox(self, text="", variable=self.app.english_mode, 
                                                             font=self.app.font_body, command=self.app.toggle_language)
        self.ui_elements['chk_english_mode'].pack(anchor="sw", padx=10, pady=10, side="bottom")

    def update_texts(self):
        """Update localized texts"""
        lang = self.app.lang
        self.ui_elements['title'].configure(text=lang.get("app_title"))
        self.ui_elements['lbl_gradient'].configure(text=lang.get("lbl_gradient"))
        self.ui_elements['btn_browse_in'].configure(text=lang.get("btn_browse"))
        self.ui_elements['lbl_output_settings'].configure(text=lang.get("lbl_output_settings"))
        self.ui_elements['chk_auto_update'].configure(text=lang.get("chk_auto_update"))
        self.ui_elements['chk_overwrite'].configure(text=lang.get("chk_overwrite"))
        self.ui_elements['chk_channel_preview'].configure(text=lang.get("chk_channel_preview"))
        self.ui_elements['lbl_output_path'].configure(text=lang.get("lbl_output_path"))
        self.ui_elements['btn_browse_out'].configure(text=lang.get("btn_browse"))
        self.ui_elements['btn_save'].configure(text=lang.get("btn_save"))
        self.ui_elements['btn_save_as'].configure(text=lang.get("btn_save_as"))
        self.ui_elements['chk_english_mode'].configure(text=lang.get("chk_english_mode"))
