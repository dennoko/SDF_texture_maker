import numpy as np
import cv2  # type: ignore
from PIL import Image
import os
from typing import Optional, Tuple, Union

class SDFProcessor:
    """Class for handling SDF texture processing logic"""
    
    def __init__(self) -> None:
        self.gradient_image: Optional[np.ndarray] = None
        self.result_image: Optional[np.ndarray] = None
    
    def load_gradient_image(self, image_path: str) -> bool:
        """
        Load gradient image from path.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            # Load with Pillow and convert to RGBA
            pil_image = Image.open(image_path).convert('RGBA')
            # Convert to NumPy array for OpenCV
            self.gradient_image = np.array(pil_image)
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def create_sdf_from_gradient(self) -> np.ndarray:
        """
        Generate SDF texture from the loaded gradient image.
        
        Returns:
            np.ndarray: Generated SDF texture as RGBA numpy array
            
        Raises:
            ValueError: If no gradient image is loaded
        """
        if self.gradient_image is None:
            raise ValueError("Gradient image not set")
        
        height, width = self.gradient_image.shape[:2]
        
        # Keep alpha channel from gradient image
        if self.gradient_image.shape[2] == 4:
            alpha = self.gradient_image[:, :, 3]
        else:
            alpha = np.ones((height, width), dtype=np.uint8) * 255
        
        # Convert gradient image to grayscale to use as mask
        if self.gradient_image.shape[2] >= 3:
            # Mean of RGB
            mask = np.mean(self.gradient_image[:, :, :3], axis=2)
        else:
            mask = self.gradient_image[:, :, 0]
        
        # Normalize mask (0-1)
        mask_normalized = mask.astype(np.float32) / 255.0
        
        # Create horizontally flipped mask
        # R channel = Right light (Flipped mask)
        mask_flipped = np.fliplr(mask_normalized)
        
        # Create SDF texture
        sdf_texture = np.zeros((height, width, 4), dtype=np.uint8)
        
        # R Channel: Right light (Flipped)
        sdf_texture[:, :, 0] = (mask_flipped * 255).astype(np.uint8)
        
        # G Channel: Left light (Original)
        sdf_texture[:, :, 1] = (mask_normalized * 255).astype(np.uint8)
        
        # B Channel: Unused (Set to 0)
        sdf_texture[:, :, 2] = 0
        
        # A Channel: Original alpha
        sdf_texture[:, :, 3] = alpha
        
        return sdf_texture
    
    def process_sdf(self) -> bool:
        """
        Execute SDF processing.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.gradient_image is None:
            return False
        
        try:
            self.result_image = self.create_sdf_from_gradient()
            return True
            
        except Exception as e:
            print(f"SDF processing error: {e}")
            return False
    
    def save_result(self, output_path: str) -> bool:
        """
        Save the result image.
        
        Args:
            output_path: Path to save result
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.result_image is None:
            return False
        
        try:
            # Convert NumPy array to PIL Image
            pil_image = Image.fromarray(self.result_image, 'RGBA')
            # Save as PNG
            pil_image.save(output_path, 'PNG')
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def get_result_for_display(self) -> Optional[Image.Image]:
        """
        Get result image for display.
        
        Returns:
            Optional[Image.Image]: PIL Image object or None
        """
        if self.result_image is None:
            return None
        
        return Image.fromarray(self.result_image, 'RGBA')
    
    def get_preview_channels(self) -> Tuple[Optional[Image.Image], Optional[Image.Image], Optional[Image.Image]]:
        """
        Get independent channel previews.
        
        Returns:
            Tuple containing (R_Channel_Image, G_Channel_Image, Combined_Image)
        """
        if self.result_image is None:
            return None, None, None
        
        # R Channel (Right Light)
        r_channel = np.zeros_like(self.result_image)
        r_channel[:, :, 0] = self.result_image[:, :, 0]
        r_channel[:, :, 3] = self.result_image[:, :, 3]  # Keep alpha
        r_image = Image.fromarray(r_channel, 'RGBA')
        
        # G Channel (Left Light)
        g_channel = np.zeros_like(self.result_image)
        g_channel[:, :, 1] = self.result_image[:, :, 1]
        g_channel[:, :, 3] = self.result_image[:, :, 3]  # Keep alpha
        g_image = Image.fromarray(g_channel, 'RGBA')
        
        # Combined
        combined = self.result_image.copy()
        combined_image = Image.fromarray(combined, 'RGBA')
        
        return r_image, g_image, combined_image
