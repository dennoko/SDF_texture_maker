import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter.font as tkfont
from PIL import Image
import os
import threading
from pathlib import Path
from watchdog.observers import Observer
import time
from typing import Dict, Optional, Any
from tkinterdnd2 import TkinterDnD, DND_FILES

from ..core.sdf_processor import SDFProcessor
from ..core.channel_processor import ChannelProcessor
from ..utils.file_watcher import FileWatcher
from ..utils import config
from ..utils.localization import LanguageManager

# Import Panels
from .panels.control_panel import ControlPanel
from .panels.channel_panel import ChannelPanel
from .panels.preview_panel import PreviewPanel

class CtkDnDAware(ctk.CTk, TkinterDnD.DnDWrapper):
    """CustomTkinter window with Drag and Drop support"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class SDFTextureApp:
    """Main application class for SDF Make Supporter"""
    
    def __init__(self):
        # Fix taskbar icon on Windows
        try:
            from ctypes import windll
            myappid = 'mycompany.sdfmakesupporter.v1' # arbitrary string
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            print(f"AppUserModelID setup failed: {e}")

        # CustomTkinter Settings
        ctk.set_appearance_mode(config.THEME_MODE)
        ctk.set_default_color_theme(config.THEME_COLOR)
        
        # Initialize Localization
        resource_path = config.get_resource_path(os.path.join("src", "resources", "strings.json"))
        self.lang = LanguageManager(resource_path)
        
        # Main Window with DnD
        self.root = CtkDnDAware()
        self.root.title(self.lang.get("app_title"))
        self.root.geometry(config.WINDOW_GEOMETRY)
        
        # Encode for Windows DnD support
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
        
        # Set Icon
        try:
            icon_path = config.get_resource_path(os.path.join("icon", "icon.ico"))
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                # Fallback for dev environment if not bundled
                dev_icon_path = os.path.join(os.getcwd(), "icon", "icon.ico")
                if os.path.exists(dev_icon_path):
                    self.root.iconbitmap(dev_icon_path)
        except Exception as e:
            print(f"Icon load error: {e}")
        
        # Setup fonts
        self.setup_fonts()
        
        # Logic Processor
        self.processor = SDFProcessor()
        self.channel_processor = ChannelProcessor()
        
        # File Watcher
        self.observer: Optional[Observer] = None
        self.auto_update = ctk.BooleanVar(value=True)
        self.overwrite_files = ctk.BooleanVar(value=True)
        self.show_channel_preview = ctk.BooleanVar(value=False)
        self.english_mode = ctk.BooleanVar(value=(self.lang.current_lang == "en"))
        
        # Path Variables
        self.gradient_path = ctk.StringVar()
        self.b_channel_path = ctk.StringVar()
        self.a_channel_path = ctk.StringVar()
        self.output_path = ctk.StringVar()
        
        # Initialize UI structure
        self.setup_ui()
        
        # Initial updates
        self.update_ui_texts() 
        
        # Window Close Protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_fonts(self):
        """Configure Windows standard fonts"""
        try:
            available_fonts = tkfont.families()
        except Exception as e:
            print(f"Font detection error: {e}")
            available_fonts = tuple(["Arial"])
        
        selected_font = "Arial"
        for font_family in config.FONT_FAMILIES:
            if font_family in available_fonts:
                selected_font = font_family
                break
        
        self.font_large = ctk.CTkFont(family=selected_font, size=20, weight="bold")
        self.font_medium = ctk.CTkFont(family=selected_font, size=16, weight="bold")
        self.font_normal = ctk.CTkFont(family=selected_font, size=12, weight="bold")
        self.font_small = ctk.CTkFont(family=selected_font, size=10)
        self.font_body = ctk.CTkFont(family=selected_font, size=11)
        
        print(f"Using font: {selected_font}")
    
    def setup_ui(self):
        """Setup UI components using panels"""
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left: Control Panel
        # Left: Control Panel
        self.control_panel = ControlPanel(main_frame, app=self)
        self.control_panel.pack(side="left", fill="y", padx=(0, 10), pady=0)

        # Add Channel Panel inside Control Panel or below it?
        # The plan was to add it via ControlPanel class, but here we instantiate ControlPanel.
        # Let's check ControlPanel implementation again.
        # ControlPanel is a Frame. We can add ChannelPanel inside ControlPanel.
        # BUT, the request said "separate file".
        # If I modify ControlPanel to include ChannelPanel, that modifies ControlPanel.
        # If I add it here in App, I need to make sure the layout is correct.
        # ControlPanel takes "modifications" well if they are external?
        # No, ControlPanel is a class.
        # Better to modify ControlPanel to include ChannelPanel.
        # Wait, the plan said "ControlPanelの末尾にChannelConfigPanelを追加する形にします".
        # So I will modify ControlPanel to instantiate ChannelPanel.
        # So NO changes here for that.

        
        # Right: Preview Panel
        self.preview_panel = PreviewPanel(main_frame, app=self)
        self.preview_panel.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
        # Initial Layout
        self.preview_panel.setup_layout()
    
    def update_ui_texts(self):
        """Update all UI texts based on current language"""
        self.root.title(self.lang.get("app_title"))
        
        # Update panels
        self.control_panel.update_texts()
        self.preview_panel.update_texts()

    def toggle_language(self):
        """Toggle language between Japanese and English"""
        new_lang = "en" if self.english_mode.get() else "ja"
        self.lang.set_language(new_lang)
        self.update_ui_texts()

    def toggle_channel_preview(self):
        """Toggle channel preview mode"""
        self.preview_panel.setup_layout()
        # Trigger image update via panel
        self.update_all_previews()
    
    def toggle_auto_update(self):
        """Toggle auto-update"""
        if self.auto_update.get():
            self.start_file_watching()
        else:
            self.stop_file_watching()
            
    def update_all_previews(self):
        """Update preview panel images"""
        # Original
        if self.processor.gradient_image is not None:
             gradient_file = self.gradient_path.get()
             if gradient_file and os.path.exists(gradient_file):
                 try:
                     original_img = Image.open(gradient_file).convert('RGBA')
                     self.preview_panel.set_image("original", original_img)
                 except Exception as e:
                     print(f"Preview update error (original): {e}")

        # Others
        if self.processor.result_image is not None:
            self.preview_panel.update_all_images(self.processor)

    # --- Logic Methods ---

    def on_drop(self, event):
        """Handle Drag and Drop event"""
        try:
            path = event.data
            if path.startswith('{') and path.endswith('}'):
                path = path[1:-1]
            
            self.gradient_path.set(path)
            self.update_output_path()
            self.load_and_preview_gradient()
        except Exception as e:
            print(f"Drop error: {e}")

    def browse_gradient(self):
        """Browse for gradient image"""
        file_path = filedialog.askopenfilename(
            title=self.lang.get("file_dialog_gradient"),
            filetypes=config.IMAGE_FILE_TYPES
        )
        if file_path:
            self.gradient_path.set(file_path)
            self.update_output_path()
            self.load_and_preview_gradient()

    def browse_extra_channel(self, channel_type: str):
        """Browse for B/A channel image"""
        file_path = filedialog.askopenfilename(
            title=f"Select {channel_type} Channel Image",
            filetypes=config.IMAGE_FILE_TYPES
        )
        if file_path:
            if channel_type == 'B':
                self.b_channel_path.set(file_path)
            elif channel_type == 'A':
                self.a_channel_path.set(file_path)
            
            self.load_extra_channel(channel_type)

    def clear_extra_channel(self, channel_type: str):
        """Clear B/A channel image"""
        if channel_type == 'B':
            self.b_channel_path.set("")
        elif channel_type == 'A':
            self.a_channel_path.set("")
            
        self.channel_processor.clear_channel(channel_type)
        self.auto_generate_sdf(auto_save=False)

    def load_extra_channel(self, channel_type: str):
        """Load extra channel and regenerate"""
        path = self.b_channel_path.get() if channel_type == 'B' else self.a_channel_path.get()
        if not path or not os.path.exists(path):
            return

        if self.channel_processor.load_image(path, channel_type):
            self.auto_generate_sdf(auto_save=False)
        else:
            print(f"Failed to load {channel_type} channel")
    
    def browse_output(self):
        """Browse for output path"""
        file_path = filedialog.asksaveasfilename(
            title=self.lang.get("file_dialog_output"),
            defaultextension=".png",
            filetypes=config.PNG_FILE_TYPE
        )
        if file_path:
            self.output_path.set(file_path)
    
    def update_output_path(self):
        """Generate output path based on input path"""
        gradient_file = self.gradient_path.get()
        if gradient_file:
            path = Path(gradient_file)
            output_file = path.parent / f"{path.stem}_SDF.png"
            self.output_path.set(str(output_file))
    
    def load_and_preview_gradient(self):
        """Load and preview the selected gradient"""
        gradient_file = self.gradient_path.get()
        if not gradient_file or not os.path.exists(gradient_file):
            return
        
        if self.processor.load_gradient_image(gradient_file):
            # Update original preview immediately
            original_img = Image.open(gradient_file).convert('RGBA')
            self.preview_panel.set_image("original", original_img)
            
            self.auto_generate_sdf(auto_save=False)
            
            if self.auto_update.get():
                self.start_file_watching()
        else:
            messagebox.showerror(self.lang.get("msg_error"), self.lang.get("msg_load_error"))
    
    def auto_generate_sdf(self, auto_save=False):
        """Automatically generate SDF"""
        try:
            if self.processor.process_sdf():
                # Apply Channel Processing
                if self.processor.result_image is not None:
                    self.processor.result_image = self.channel_processor.process_channels(self.processor.result_image)

                self.update_all_previews()
                print("SDF texture auto-generated")
                
                if auto_save:
                    output_file = self.output_path.get()
                    if output_file:
                        if self.processor.save_result(output_file):
                            print(f"Auto-save complete: {output_file}")
                        else:
                            print("Auto-save failed")
            else:
                print("SDF auto-generation failed")
        except Exception as e:
            print(f"SDF auto-gen error: {str(e)}")
    
    def save_as_result(self):
        """Save As..."""
        if self.processor.result_image is None:
            messagebox.showerror(self.lang.get("msg_error"), self.lang.get("msg_no_image_save"))
            return
        
        output_file = filedialog.asksaveasfilename(
            title=self.lang.get("file_dialog_save_as"),
            defaultextension=".png",
            filetypes=config.PNG_FILE_TYPE,
            initialdir=os.path.dirname(self.output_path.get()) if self.output_path.get() else None,
            initialfile=os.path.basename(self.output_path.get()) if self.output_path.get() else "SDF_texture.png"
        )
        
        if not output_file:
            return
        
        if self.processor.save_result(output_file):
            messagebox.showinfo(self.lang.get("msg_success"), self.lang.get("msg_save_complete", output_file))
            self.output_path.set(output_file)
        else:
            messagebox.showerror(self.lang.get("msg_error"), self.lang.get("msg_save_failed"))

    def save_result(self):
        """Save result to current path"""
        if self.processor.result_image is None:
            messagebox.showerror(self.lang.get("msg_error"), self.lang.get("msg_no_image_save"))
            return
        
        output_file = self.output_path.get()
        if not output_file:
            messagebox.showerror(self.lang.get("msg_error"), self.lang.get("msg_save_failed"))
            return
        
        if os.path.exists(output_file) and not self.overwrite_files.get():
            if not messagebox.askyesno(self.lang.get("msg_error"), self.lang.get("msg_overwrite_confirm", output_file)):
                return
        
        if self.processor.save_result(output_file):
            messagebox.showinfo(self.lang.get("msg_success"), self.lang.get("msg_save_complete", output_file))
        else:
            messagebox.showerror(self.lang.get("msg_error"), self.lang.get("msg_save_failed"))
    
    def start_file_watching(self):
        """Start file watcher"""
        gradient_file = self.gradient_path.get()
        if not gradient_file or not os.path.exists(gradient_file):
            self.auto_update.set(False)
            messagebox.showwarning(self.lang.get("msg_error"), self.lang.get("msg_load_error"))
            return
        
        self.stop_file_watching()
        
        try:
            self.observer = Observer()
            event_handler = FileWatcher(self.auto_process, gradient_file)
            watch_dir = os.path.dirname(gradient_file)
            self.observer.schedule(event_handler, watch_dir, recursive=False)
            self.observer.start()
            print(f"Started watching: {gradient_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start file watcher: {str(e)}")
            self.auto_update.set(False)
    
    def stop_file_watching(self):
        """Stop file watcher"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            print("Stopped file watching")
    
    def auto_process(self):
        """Callback for file watcher"""
        def process():
            try:
                time.sleep(0.5)
                
                gradient_file = self.gradient_path.get()
                if not self.processor.load_gradient_image(gradient_file):
                    print("Auto-process: Failed to reload image")
                    return
                # Update original preview immediately
                original_img = Image.open(gradient_file).convert('RGBA')
                self.preview_panel.set_image("original", original_img)
                
                if self.processor.process_sdf():
                    self.update_all_previews()
                    print("Auto-process: SDF regenerated")
                    
                    output_file = self.output_path.get()
                    if output_file:
                        if self.processor.save_result(output_file):
                            print(f"Auto-saved: {output_file}")
                        else:
                            print("Auto-save failed")
                else:
                    print("Auto-process: SDF generation failed")
            except Exception as e:
                print(f"Auto-process error: {e}")
        
        self.root.after(100, process)
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_file_watching()
        self.root.destroy()
    
    def run(self):
        """Run the app"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SDFTextureApp()
    app.run()
