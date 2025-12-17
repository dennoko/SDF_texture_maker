import customtkinter as ctk
from PIL import Image, ImageTk
from typing import TYPE_CHECKING, Dict, Any, Optional

if TYPE_CHECKING:
    from ..app import SDFTextureApp

class PreviewPanel(ctk.CTkFrame):
    """Right side preview panel with responsive grid"""
    
    def __init__(self, parent, app: "SDFTextureApp", **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.preview_images: Dict[str, ctk.CTkLabel] = {}
        self.raw_images: Dict[str, Optional[Image.Image]] = {
            "original": None,
            "r_channel": None,
            "g_channel": None,
            "combined": None
        }
        self.preview_frames: Dict[str, ctk.CTkFrame] = {}
        
        self.ui_elements: Dict[str, Any] = {}
        
        self._setup_structure()
        
        # Bind resize event
        self.container.bind('<Configure>', self._on_resize)
        self._resize_timer = None
        
    def _setup_structure(self):
        self.ui_elements['lbl_preview'] = ctk.CTkLabel(self, text="", font=self.app.font_medium)
        self.ui_elements['lbl_preview'].pack(pady=(10, 10))
        
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
    def setup_layout(self):
        """Build the grid layout based on current mode"""
        for widget in self.container.winfo_children():
            widget.destroy()
        self.preview_frames.clear()
        self.preview_images.clear()
        
        show_channels = self.app.show_channel_preview.get()
        
        if show_channels:
            # 2x2 Grid
            self.container.grid_columnconfigure(0, weight=1)
            self.container.grid_columnconfigure(1, weight=1)
            self.container.grid_rowconfigure(0, weight=1)
            self.container.grid_rowconfigure(1, weight=1)
            
            # Reset
            for i in range(2, 4):
                self.container.grid_columnconfigure(i, weight=0)
                self.container.grid_rowconfigure(i, weight=0)
            
            self._create_cell("lbl_preview_original", 0, 0, "original")
            self._create_cell("lbl_preview_r", 0, 1, "r_channel")
            self._create_cell("lbl_preview_g", 1, 0, "g_channel")
            self._create_cell("lbl_preview_combined", 1, 1, "combined")
        else:
            # 1x2 Grid
            self.container.grid_columnconfigure(0, weight=1)
            self.container.grid_columnconfigure(1, weight=1)
            self.container.grid_rowconfigure(0, weight=1)
            
            # Reset
            for i in range(2, 4):
                self.container.grid_columnconfigure(i, weight=0)
            for i in range(1, 4):
                self.container.grid_rowconfigure(i, weight=0)
            
            self._create_cell("lbl_preview_original", 0, 0, "original")
            self._create_cell("lbl_preview_combined", 0, 1, "combined")
            
        # Refill images if they exist
        # Wait for layout to calculate sizes
        self.after(100, self._refresh_images)

    def _create_cell(self, title_key, row, col, key):
        frame = ctk.CTkFrame(self.container)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        lbl_title = ctk.CTkLabel(frame, text=self.app.lang.get(title_key), font=self.app.font_normal)
        lbl_title.pack(pady=(5, 0))
        # Keep reference to update title later
        self.ui_elements[f"title_{key}"] = lbl_title
        self.ui_elements[f"title_key_{key}"] = title_key # Store key for lang update
        
        # Image Label holder
        img_label = ctk.CTkLabel(frame, text=self.app.lang.get("lbl_no_image"), font=self.app.font_body)
        img_label.pack(padx=2, pady=2, expand=True) # expand=True to center
        
        self.preview_images[key] = img_label
        self.preview_frames[key] = frame

    def update_texts(self):
        """Update localized texts"""
        self.ui_elements['lbl_preview'].configure(text=self.app.lang.get("lbl_preview"))
        
        # Update cell titles
        for key, lbl in self.ui_elements.items():
            if key.startswith("title_") and not key.startswith("title_key_"):
                # extract real key suffix
                real_key = key.replace("title_", "")
                lang_key_store = f"title_key_{real_key}"
                if lang_key_store in self.ui_elements:
                    lang_key = self.ui_elements[lang_key_store]
                    lbl.configure(text=self.app.lang.get(lang_key))
        
        # Update "No Image" text if no image is present? 
        # Actually logic is: if image exists, remove text. If not, set text "No Image".
        # We can re-run _refresh_images which handles this.
        self._refresh_images()

    def set_image(self, key: str, pil_image: Optional[Image.Image]):
        """Set raw image content"""
        # Store copy of raw image
        if pil_image:
            self.raw_images[key] = pil_image.copy()
        else:
            self.raw_images[key] = None
        
        # Trigger redraw
        self._refresh_single_image(key)

    def update_all_images(self, processor):
        """Pull all images from processor"""
        r, g, c = processor.get_preview_channels()
        self.set_image("r_channel", r)
        self.set_image("g_channel", g)
        self.set_image("combined", c)

    def _on_resize(self, event):
        """Handle resize with debounce"""
        if self._resize_timer:
            self.after_cancel(self._resize_timer)
        self._resize_timer = self.after(100, self._perform_resize)

    def _perform_resize(self):
        self._refresh_images()

    def _refresh_images(self):
        """Redraw all active images based on current container size"""
        for key in self.preview_images.keys():
            self._refresh_single_image(key)

    def _refresh_single_image(self, key):
        if key not in self.preview_images:
            return
            
        lbl = self.preview_images[key]
        raw = self.raw_images[key]
        
        if raw is None:
            lbl.configure(image=None, text=self.app.lang.get("lbl_no_image"))
            return
            
        # Calculate size
        # We need the size of the *frame* holding the label, or the grid cell.
        # self.preview_frames[key] is the cell frame.
        frame = self.preview_frames[key]
        
        # Determine available w/h
        # frame.update_idletasks() # Force update? Might be slow.
        w = frame.winfo_width()
        h = frame.winfo_height()
        
        # Subtract some padding/title height
        # Title is approx 30px? Padding 10px?
        w_avail = w - 20
        h_avail = h - 40 
        
        if w_avail < 10 or h_avail < 10:
            return
            
        # Fit square
        size = min(w_avail, h_avail)
        
        # Resize
        try:
            # High quality resize
            resized = raw.copy().resize((size, size), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized)
            
            lbl.configure(image=photo, text="")
            lbl.image = photo # Keep reference
        except Exception as e:
            print(f"Resize error for {key}: {e}")
