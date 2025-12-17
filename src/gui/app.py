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

from ..core.sdf_processor import SDFProcessor
from ..utils.file_watcher import FileWatcher
from ..utils import config

class SDFTextureApp:
    """Main application class for SDF Texture Maker"""
    
    def __init__(self):
        # CustomTkinter Settings
        ctk.set_appearance_mode(config.THEME_MODE)
        ctk.set_default_color_theme(config.THEME_COLOR)
        
        # Main Window
        self.root = ctk.CTk()
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(config.WINDOW_GEOMETRY)
        
        # Setup fonts
        self.setup_fonts()
        
        # Logic Processor
        self.processor = SDFProcessor()
        
        # File Watcher
        self.observer: Optional[Observer] = None
        self.auto_update = ctk.BooleanVar(value=True)
        self.overwrite_files = ctk.BooleanVar(value=True)
        self.show_channel_preview = ctk.BooleanVar(value=False)
        
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
        
        self.setup_ui()
        
        # Window Close Protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_fonts(self):
        """Configure Windows standard fonts"""
        try:
            available_fonts = tkfont.families()
        except Exception as e:
            print(f"Font detection error: {e}")
            available_fonts = tuple(["Arial"])
        
        # Select first available font
        selected_font = "Arial"
        for font_family in config.FONT_FAMILIES:
            if font_family in available_fonts:
                selected_font = font_family
                break
        
        # Create font objects
        self.font_large = ctk.CTkFont(family=selected_font, size=20, weight="bold")
        self.font_medium = ctk.CTkFont(family=selected_font, size=16, weight="bold")
        self.font_normal = ctk.CTkFont(family=selected_font, size=12, weight="bold")
        self.font_small = ctk.CTkFont(family=selected_font, size=10)
        self.font_body = ctk.CTkFont(family=selected_font, size=11)
        
        print(f"Using font: {selected_font}")
    
    def setup_ui(self):
        """Setup UI components"""
        # Main Frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left: Control Panel
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(side="left", fill="y", padx=(0, 10), pady=0)
        
        # Right: Preview Area
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
        self.setup_control_panel(control_frame)
        self.setup_preview_area(preview_frame)
    
    def setup_control_panel(self, parent):
        """Setup Control Panel"""
        # Title
        title_label = ctk.CTkLabel(parent, text="SDF Texture Maker", 
                                  font=self.font_large)
        title_label.pack(pady=(10, 20))
        
        # Input Section
        input_section = ctk.CTkFrame(parent)
        input_section.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(input_section, text="Gradient Image", 
                    font=self.font_normal).pack(anchor="w", padx=10, pady=(10, 5))
        
        input_frame = ctk.CTkFrame(input_section)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.gradient_entry = ctk.CTkEntry(input_frame, textvariable=self.gradient_path)
        self.gradient_entry.pack(side="left", fill="x", expand=True, padx=(5, 5), pady=5)
        
        ctk.CTkButton(input_frame, text="Browse", width=60, font=self.font_body,
                     command=self.browse_gradient).pack(side="right", padx=(0, 5), pady=5)
        
        # Output Section
        output_section = ctk.CTkFrame(parent)
        output_section.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(output_section, text="Output Settings", 
                    font=self.font_normal).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Checkboxes
        ctk.CTkCheckBox(output_section, text="Auto Update on File Change",
                        variable=self.auto_update,
                        font=self.font_body,
                        command=self.toggle_auto_update).pack(anchor="w", padx=10, pady=5)
        
        ctk.CTkCheckBox(output_section, text="Overwrite Existing Files",
                        variable=self.overwrite_files,
                        font=self.font_body).pack(anchor="w", padx=10, pady=5)
        
        ctk.CTkCheckBox(output_section, text="Show Channel Previews",
                        variable=self.show_channel_preview,
                        font=self.font_body,
                        command=self.toggle_channel_preview).pack(anchor="w", padx=10, pady=5)
        
        # Output Path
        output_frame = ctk.CTkFrame(output_section)
        output_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        ctk.CTkLabel(output_frame, text="Output Path:", font=self.font_body).pack(anchor="w", padx=5, pady=(5, 0))
        
        path_frame = ctk.CTkFrame(output_frame)
        path_frame.pack(fill="x", padx=5, pady=5)
        
        self.output_entry = ctk.CTkEntry(path_frame, textvariable=self.output_path)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(5, 5), pady=5)
        
        ctk.CTkButton(path_frame, text="Browse", width=60, font=self.font_body,
                     command=self.browse_output).pack(side="right", padx=(0, 5), pady=5)
        
        # Buttons
        ctk.CTkButton(parent, text="Save", height=35, font=self.font_body,
                     command=self.save_result).pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkButton(parent, text="Save As...", height=35, font=self.font_body,
                     command=self.save_as_result).pack(fill="x", padx=10, pady=(5, 20))
    
    def setup_preview_area(self, parent):
        """Setup Preview Area"""
        ctk.CTkLabel(parent, text="Preview", 
                    font=self.font_medium).pack(pady=(10, 10))
        
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
            
            # Reset extra
            for i in range(2, 4):
                self.preview_container.grid_columnconfigure(i, weight=0)
                self.preview_container.grid_rowconfigure(i, weight=0)
            
            self.setup_preview_frame(self.preview_container, "Original", 0, 0, "original")
            self.setup_preview_frame(self.preview_container, "R Channel (Right Light)", 0, 1, "r_channel")
            self.setup_preview_frame(self.preview_container, "G Channel (Left Light)", 1, 0, "g_channel")
            self.setup_preview_frame(self.preview_container, "Combined", 1, 1, "combined")
        else:
            # 1x2 Grid
            self.preview_container.grid_columnconfigure(0, weight=1)
            self.preview_container.grid_columnconfigure(1, weight=1)
            self.preview_container.grid_rowconfigure(0, weight=1)
            
            # Reset extra
            for i in range(2, 4):
                self.preview_container.grid_columnconfigure(i, weight=0)
            for i in range(1, 4):
                self.preview_container.grid_rowconfigure(i, weight=0)
            
            self.setup_preview_frame(self.preview_container, "Original", 0, 0, "original")
            self.setup_preview_frame(self.preview_container, "Combined", 0, 1, "combined")
    
    def setup_preview_frame(self, parent, title, row, col, key):
        """Setup individual preview frame"""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(frame, text=title, font=self.font_normal).pack(pady=(10, 5))
        
        img_label = ctk.CTkLabel(frame, text="No Image", width=250, height=200, font=self.font_body)
        img_label.pack(padx=10, pady=(0, 10), expand=True)
        
        self.preview_images[key] = img_label
        self.preview_frames[key] = frame
    
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
    
    def browse_gradient(self):
        """Browse for gradient image"""
        file_path = filedialog.askopenfilename(
            title="Select Gradient Image",
            filetypes=config.IMAGE_FILE_TYPES
        )
        if file_path:
            self.gradient_path.set(file_path)
            self.update_output_path()
            self.load_and_preview_gradient()
    
    def browse_output(self):
        """Browse for output path"""
        file_path = filedialog.asksaveasfilename(
            title="Select Output Path",
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
            
            # Auto Generate
            self.auto_generate_sdf(auto_save=False)
            
            if self.auto_update.get():
                self.start_file_watching()
        else:
            messagebox.showerror("Error", "Failed to load gradient image")
    
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
            messagebox.showerror("Error", "No image to save. Run SDF processing first.")
            return
        
        output_file = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".png",
            filetypes=config.PNG_FILE_TYPE,
            initialdir=os.path.dirname(self.output_path.get()) if self.output_path.get() else None,
            initialfile=os.path.basename(self.output_path.get()) if self.output_path.get() else "SDF_texture.png"
        )
        
        if not output_file:
            return
        
        if self.processor.save_result(output_file):
            messagebox.showinfo("Success", f"Saved to: {output_file}")
            self.output_path.set(output_file)
        else:
            messagebox.showerror("Error", "Failed to save")
    
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
        # Use copy to avoid modifying original if it's reused (though here we pass fresh images usually)
        img_copy = pil_image.copy()
        img_copy.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(img_copy)
        
        self.preview_images[key].configure(image=photo, text="")
        self.preview_images[key].image = photo
    
    def save_result(self):
        """Save result to current path"""
        if self.processor.result_image is None:
            messagebox.showerror("Error", "No image to save. Run SDF processing first.")
            return
        
        output_file = self.output_path.get()
        if not output_file:
            messagebox.showerror("Error", "Please specify output path")
            return
        
        if os.path.exists(output_file) and not self.overwrite_files.get():
            if not messagebox.askyesno("Confirm", f"File '{output_file}' exists. Overwrite?"):
                return
        
        if self.processor.save_result(output_file):
            messagebox.showinfo("Success", f"Saved to: {output_file}")
        else:
            messagebox.showerror("Error", "Failed to save")
    
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
            messagebox.showwarning("Warning", "No gradient image selected")
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
                time.sleep(0.5) # Wait for write
                
                gradient_file = self.gradient_path.get()
                # Reload even if load_gradient_image returns logic obj, we need UI update
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
