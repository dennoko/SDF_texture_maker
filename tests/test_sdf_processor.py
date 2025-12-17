import unittest
import numpy as np
from src.core.sdf_processor import SDFProcessor

class TestSDFProcessor(unittest.TestCase):
    
    def setUp(self):
        self.processor = SDFProcessor()
    
    def test_initial_state(self):
        self.assertIsNone(self.processor.gradient_image)
        self.assertIsNone(self.processor.result_image)
    
    def test_create_sdf_from_gradient_error(self):
        with self.assertRaises(ValueError):
            self.processor.create_sdf_from_gradient()
    
    def test_sdf_generation_logic(self):
        # Create a simple 2x2 gradient image
        # Top-left and Bottom-left: Black (0)
        # Top-right and Bottom-right: White (255)
        # So it's a horizontal gradient
        width, height = 4, 1
        gradient = np.zeros((height, width, 4), dtype=np.uint8)
        
        # [0, 85, 170, 255]
        for i in range(width):
            val = int(i * 255 / (width - 1))
            gradient[0, i] = [val, val, val, 255]
            
        self.processor.gradient_image = gradient
        
        result = self.processor.create_sdf_from_gradient()
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, (height, width, 4))
        
        # Check G Channel (Left Light) - Should be same as mask/gradient
        # 0 -> 0, 255 -> 255
        self.assertEqual(result[0, 0, 1], 0)
        self.assertEqual(result[0, 3, 1], 255)
        
        # Check R Channel (Right Light) - Should be flipped
        # 0 -> 255, 255 -> 0
        self.assertEqual(result[0, 0, 0], 255)
        self.assertEqual(result[0, 3, 0], 0)
        
        # Check B Channel - Should be 0
        self.assertTrue(np.all(result[:, :, 2] == 0))
        
        # Check Alpha - Should be 255
        self.assertTrue(np.all(result[:, :, 3] == 255))
        
if __name__ == '__main__':
    unittest.main()
