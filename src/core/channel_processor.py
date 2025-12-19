import numpy as np
from PIL import Image
from typing import Optional, Tuple
import os

class ChannelProcessor:
    """Processor for handling individual channel image inputs (B and A channels)"""
    
    def __init__(self):
        self.b_channel_image: Optional[np.ndarray] = None
        self.a_channel_image: Optional[np.ndarray] = None
        
    def load_image(self, path: str, channel_type: str) -> bool:
        """
        Load an image for a specific channel.
        
        Args:
            path: Path to the image file
            channel_type: 'B' or 'A'
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            pil_image = Image.open(path).convert('L') # Convert to grayscale
            image_array = np.array(pil_image)
            
            if channel_type == 'B':
                self.b_channel_image = image_array
            elif channel_type == 'A':
                self.a_channel_image = image_array
            else:
                return False
                
            return True
        except Exception as e:
            print(f"Error loading {channel_type} channel image: {e}")
            return False

    def clear_channel(self, channel_type: str):
        """Clear the loaded image for a specific channel"""
        if channel_type == 'B':
            self.b_channel_image = None
        elif channel_type == 'A':
            self.a_channel_image = None
            
    def process_channels(self, base_sdf: np.ndarray) -> np.ndarray:
        """
        Overlay B and A channel images onto the base SDF texture.
        Resizes channel images to match base_sdf dimensions if necessary.
        
        Args:
            base_sdf: The generated SDF texture (RGBA numpy array)
            
        Returns:
            np.ndarray: Modified SDF texture
        """
        if base_sdf is None:
            return None
            
        height, width = base_sdf.shape[:2]
        result_sdf = base_sdf.copy()
        
        # Process B Channel
        if self.b_channel_image is not None:
             b_resized = self._resize_to_match(self.b_channel_image, width, height)
             result_sdf[:, :, 2] = b_resized
             
        # Process A Channel
        if self.a_channel_image is not None:
            a_resized = self._resize_to_match(self.a_channel_image, width, height)
            result_sdf[:, :, 3] = a_resized
            
        return result_sdf

    def _resize_to_match(self, image: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
        """Resize image array to match target dimensions"""
        if image.shape[0] == target_height and image.shape[1] == target_width:
            return image
            
        # Use simple interpolation for resizing (matching typical texture needs)
        # Convert back to PIL for easy resizing
        pil_img = Image.fromarray(image)
        resized_pil = pil_img.resize((target_width, target_height), Image.BILINEAR)
        return np.array(resized_pil)
