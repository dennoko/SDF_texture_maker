import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter.font as tkfont
from PIL import Image, ImageTk
import os
import threading
from pathlib import Path
from watchdog.observers import Observer
import time
from typing import Dict, Optional, Any
from tkinterdnd2 import TkinterDnD, DND_FILES

from ..core.sdf_processor import SDFProcessor
from ..utils.file_watcher import FileWatcher
from ..utils import config
from ..utils.localization import LanguageManager

class CtkDnDAware(ctk.CTk, TkinterDnD.DnDWrapper):
    """CustomTkinter window with Drag and Drop support"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class SDFTextureApp:
    """Main application class for SDF Texture Maker"""
    
    def __init__(self):
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
        
        # Setup fonts
        self.setup_fonts()
        
        # Logic Processor
        self.processor = SDFProcessor()
        
        # File Watcher
        self.observer: Optional[Observer] = None
        self.auto_update = ctk.BooleanVar(value=True)
        self.overwrite_files = ctk.BooleanVar(value=True)
        self.show_channel_preview = ctk.BooleanVar(value=False)
        self.english_mode = ctk.BooleanVar(value=(self.lang.current_lang == "en"))
        
        # Path Variables
        self.gradient_path = ctk.StringVar()
        self.output_path = ctk.StringVar()
        
        # Preview Images
        self.preview_images: Dict[str, Any] = {
            "original": None, 
            "r_channel": None, 
            "g_channel": None, 
            "combined": None
        }
        
        # Preview Frames
        self.preview_frames: Dict[str, Any] = {}
        
        # UI Element References (for localization updates)
        self.ui_elements: Dict[str, Any] = {}
        
        self.setup_ui()
        self.update_ui_texts() # Initial text set
        
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
        """Setup UI components"""
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(side="left", fill="y", padx=(0, 10), pady=0)
        
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
        self.setup_control_panel(control_frame)
        self.setup_preview_area(preview_frame)
    
    def setup_control_panel(self, parent):
        """Setup Control Panel"""
        # Title
        self.ui_elements['title'] = ctk.CTkLabel(parent, text="", font=self.font_large)
        self.ui_elements['title'].pack(pady=(10, 20))
        
        # Input Section
        input_section = ctk.CTkFrame(parent)
        input_section.pack(fill="x", padx=10, pady=5)
        
        self.ui_elements['lbl_gradient'] = ctk.CTkLabel(input_section, text="", font=self.font_normal)
        self.ui_elements['lbl_gradient'].pack(anchor="w", padx=10, pady=(10, 5))
        
        input_frame = ctk.CTkFrame(input_section)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.gradient_entry = ctk.CTkEntry(input_frame, textvariable=self.gradient_path)
        self.gradient_entry.pack(side="left", fill="x", expand=True, padx=(5, 5), pady=5)
        
        self.ui_elements['btn_browse_in'] = ctk.CTkButton(input_frame, text="", width=60, font=self.font_body,
                     command=self.browse_gradient)
        self.ui_elements['btn_browse_in'].pack(side="right", padx=(0, 5), pady=5)
        
        # Output Section
        output_section = ctk.CTkFrame(parent)
        output_section.pack(fill="x", padx=10, pady=5)
        
        self.ui_elements['lbl_output_settings'] = ctk.CTkLabel(output_section, text="", font=self.font_normal)
        self.ui_elements['lbl_output_settings'].pack(anchor="w", padx=10, pady=(10, 5))
        
        # Checkboxes
        self.ui_elements['chk_auto_update'] = ctk.CTkCheckBox(
            output_section, text="", variable=self.auto_update, font=self.font_body, command=self.toggle_auto_update)
        self.ui_elements['chk_auto_update'].pack(anchor="w", padx=10, pady=5)
        
        self.ui_elements['chk_overwrite'] = ctk.CTkCheckBox(
            output_section, text="", variable=self.overwrite_files, font=self.font_body)
        self.ui_elements['chk_overwrite'].pack(anchor="w", padx=10, pady=5)
        
        self.ui_elements['chk_channel_preview'] = ctk.CTkCheckBox(
            output_section, text="", variable=self.show_channel_preview, font=self.font_body, command=self.toggle_channel_preview)
        self.ui_elements['chk_channel_preview'].pack(anchor="w", padx=10, pady=5)
        
        # Output Path
        output_frame = ctk.CTkFrame(output_section)
        output_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.ui_elements['lbl_output_path'] = ctk.CTkLabel(output_frame, text="", font=self.font_body)
        self.ui_elements['lbl_output_path'].pack(anchor="w", padx=5, pady=(5, 0))
        
        path_frame = ctk.CTkFrame(output_frame)
        path_frame.pack(fill="x", padx=5, pady=5)
        
        self.output_entry = ctk.CTkEntry(path_frame, textvariable=self.output_path)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(5, 5), pady=5)
        
        self.ui_elements['btn_browse_out'] = ctk.CTkButton(path_frame, text="", width=60, font=self.font_body,
                     command=self.browse_output)
        self.ui_elements['btn_browse_out'].pack(side="right", padx=(0, 5), pady=5)
        
        # Buttons
        self.ui_elements['btn_save'] = ctk.CTkButton(parent, text="", height=35, font=self.font_body,
                     command=self.save_result)
        self.ui_elements['btn_save'].pack(fill="x", padx=10, pady=(10, 5))
        
        self.ui_elements['btn_save_as'] = ctk.CTkButton(parent, text="", height=35, font=self.font_body,
                     command=self.save_as_result)
        self.ui_elements['btn_save_as'].pack(fill="x", padx=10, pady=(5, 20))
        
        # Language Switcher
        self.ui_elements['chk_english_mode'] = ctk.CTkCheckBox(parent, text="", variable=self.english_mode, 
                                                             font=self.font_body, command=self.toggle_language)
        self.ui_elements['chk_english_mode'].pack(anchor="sw", padx=10, pady=10, side="bottom")

    def setup_preview_area(self, parent):
        """Setup Preview Area"""
        self.ui_elements['lbl_preview'] = ctk.CTkLabel(parent, text="", font=self.font_medium)
        self.ui_elements['lbl_preview'].pack(pady=(10, 10))
        
        self.preview_container = ctk.CTkFrame(parent)
        self.preview_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.setup_preview_layout()
    
    def setup_preview_layout(self):
        """Configure Preview Grid Layout"""
        for widget in self.preview_container.winfo_children():
            widget.destroy()
        self.preview_frames.clear()
        self.preview_images.clear()
        
        if self.show_channel_preview.get():
            # 2x2 Grid
            self.preview_container.grid_columnconfigure(0, weight=1)
            self.preview_container.grid_columnconfigure(1, weight=1)
            self.preview_container.grid_rowconfigure(0, weight=1)
            self.preview_container.grid_rowconfigure(1, weight=1)
            
            for i in range(2, 4):
                self.preview_container.grid_columnconfigure(i, weight=0)
                self.preview_container.grid_rowconfigure(i, weight=0)
            
            self.setup_preview_frame(self.preview_container, "lbl_preview_original", 0, 0, "original")
            self.setup_preview_frame(self.preview_container, "lbl_preview_r", 0, 1, "r_channel")
            self.setup_preview_frame(self.preview_container, "lbl_preview_g", 1, 0, "g_channel")
            self.setup_preview_frame(self.preview_container, "lbl_preview_combined", 1, 1, "combined")
        else:
            # 1x2 Grid
            self.preview_container.grid_columnconfigure(0, weight=1)
            self.preview_container.grid_columnconfigure(1, weight=1)
            self.preview_container.grid_rowconfigure(0, weight=1)
            
            for i in range(2, 4):
                self.preview_container.grid_columnconfigure(i, weight=0)
            for i in range(1, 4):
                self.preview_container.grid_rowconfigure(i, weight=0)
            
            self.setup_preview_frame(self.preview_container, "lbl_preview_original", 0, 0, "original")
            self.setup_preview_frame(self.preview_container, "lbl_preview_combined", 0, 1, "combined")
    
    def setup_preview_frame(self, parent, title_key, row, col, key):
        """Setup individual preview frame"""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # Create dynamic label
        lbl = ctk.CTkLabel(frame, text=self.lang.get(title_key), font=self.font_normal)
        lbl.pack(pady=(10, 5))
        
        # Store for translation
        # Note: Since the preview layout is rebuilt, we need to track these dynamically
        # or just set text once on creation since setup_preview_layout is called on refresh?
        # Actually it's cleaner to just set it here. If language changes, setup_preview_layout can be called.
        
        img_label = ctk.CTkLabel(frame, text=self.lang.get("lbl_no_image"), width=250, height=200, font=self.font_body)
        img_label.pack(padx=10, pady=(0, 10), expand=True)
        
        self.preview_images[key] = img_label
        self.preview_frames[key] = frame
    
    def update_ui_texts(self):
        """Update all UI texts based on current language"""
        self.root.title(self.lang.get("app_title"))
        
        # Control Panel
        self.ui_elements['title'].configure(text=self.lang.get("app_title"))
        self.ui_elements['lbl_gradient'].configure(text=self.lang.get("lbl_gradient"))
        self.ui_elements['btn_browse_in'].configure(text=self.lang.get("btn_browse"))
        self.ui_elements['lbl_output_settings'].configure(text=self.lang.get("lbl_output_settings"))
        self.ui_elements['chk_auto_update'].configure(text=self.lang.get("chk_auto_update"))
        self.ui_elements['chk_overwrite'].configure(text=self.lang.get("chk_overwrite"))
        self.ui_elements['chk_channel_preview'].configure(text=self.lang.get("chk_channel_preview"))
        self.ui_elements['lbl_output_path'].configure(text=self.lang.get("lbl_output_path"))
        self.ui_elements['btn_browse_out'].configure(text=self.lang.get("btn_browse"))
        self.ui_elements['btn_save'].configure(text=self.lang.get("btn_save"))
        self.ui_elements['btn_save_as'].configure(text=self.lang.get("btn_save_as"))
        self.ui_elements['lbl_preview'].configure(text=self.lang.get("lbl_preview"))
        self.ui_elements['chk_english_mode'].configure(text=self.lang.get("chk_english_mode"))
        
        # Rebuild preview layout to update titles
        self.setup_preview_layout()
        
        if self.processor.result_image is not None or self.processor.gradient_image is not None:
             # Refresh images if they exist (images stay, but "No Image" text needs update if empty?)
             # Actually setup_preview_layout clears images, so we need to reload them to labels
             self.update_all_previews()
             if self.processor.gradient_image is not None:
                 # Need to re-set original image
                 if os.path.exists(self.gradient_path.get()):
                     img = Image.open(self.gradient_path.get()).convert('RGBA')
                     self.update_preview_image("original", img)

    def toggle_channel_preview(self):
        """Toggle channel preview mode"""
        self.setup_preview_layout()
        
        if self.processor.gradient_image is not None:
            gradient_file = self.gradient_path.get()
            if gradient_file and os.path.exists(gradient_file):
                original_img = Image.open(gradient_file).convert('RGBA')
                self.update_preview_image("original", original_img)
        
        if self.processor.result_image is not None:
            self.update_all_previews()

    def toggle_language(self):
        """Toggle language between Japanese and English"""
        new_lang = "en" if self.english_mode.get() else "ja"
        self.lang.set_language(new_lang)
        self.update_ui_texts()
        
    def on_drop(self, event):
        """Handle Drag and Drop event"""
        try:
            # Windows path handling (tkinterdnd2 returns paths wrapped in curly braces if they contain spaces)
            path = event.data
            if path.startswith('{') and path.endswith('}'):
                path = path[1:-1]
            
            # If multiple files dropped, take the first one? tkinterdnd2 usually returns list if spaces?
            # Actually on Windows it might be space separated if multiple?
            # For simplicity, assume one file or handle curly braces simple case
            
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
            original_img = Image.open(gradient_file).convert('RGBA')
            self.update_preview_image("original", original_img)
            
            self.auto_generate_sdf(auto_save=False)
            
            if self.auto_update.get():
                self.start_file_watching()
        else:
            messagebox.showerror(self.lang.get("msg_error"), self.lang.get("msg_load_error"))
    
    def auto_generate_sdf(self, auto_save=False):
        """Automatically generate SDF"""
        try:
            if self.processor.process_sdf():
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
    
    def update_all_previews(self):
        """Update all preview images"""
        if self.processor.result_image is None:
            return
        
        r_img, g_img, combined_img = self.processor.get_preview_channels()
        
        if self.show_channel_preview.get():
            if r_img: self.update_preview_image("r_channel", r_img)
            if g_img: self.update_preview_image("g_channel", g_img)
        
        if combined_img:
            self.update_preview_image("combined", combined_img)
    
    def update_preview_image(self, key, pil_image):
        """Update a specific preview image"""
        if key not in self.preview_frames:
            return
        if key not in self.preview_images or self.preview_images[key] is None:
            return
        
        display_size = (200, 200)
        img_copy = pil_image.copy()
        img_copy.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(img_copy)
        
        self.preview_images[key].configure(image=photo, text="")
        self.preview_images[key].image = photo
    
    def save_result(self):
        """Save result to current path"""
        if self.processor.result_image is None:
            messagebox.showerror(self.lang.get("msg_error"), self.lang.get("msg_no_image_save"))
            return
        
        output_file = self.output_path.get()
        if not output_file:
            messagebox.showerror(self.lang.get("msg_error"), self.lang.get("msg_save_failed")) # Generic error for no path
            return
        
        if os.path.exists(output_file) and not self.overwrite_files.get():
            # Using format for message
            if not messagebox.askyesno(self.lang.get("msg_error"), self.lang.get("msg_overwrite_confirm", output_file)):
                return
        
        if self.processor.save_result(output_file):
            messagebox.showinfo(self.lang.get("msg_success"), self.lang.get("msg_save_complete", output_file))
        else:
            messagebox.showerror(self.lang.get("msg_error"), self.lang.get("msg_save_failed"))
    
    def toggle_auto_update(self):
        """Toggle auto-update"""
        if self.auto_update.get():
            self.start_file_watching()
        else:
            self.stop_file_watching()
    
    def start_file_watching(self):
        """Start file watcher"""
        gradient_file = self.gradient_path.get()
        if not gradient_file or not os.path.exists(gradient_file):
            self.auto_update.set(False)
            messagebox.showwarning(self.lang.get("msg_error"), self.lang.get("msg_load_error")) # Reusing load error
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
                
                original_img = Image.open(gradient_file).convert('RGBA')
                self.update_preview_image("original", original_img)
                
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
