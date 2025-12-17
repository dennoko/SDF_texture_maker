from PIL import Image
import os

def create_ico():
    src_path = os.path.join("icon", "icon_2.png")
    dst_path = os.path.join("icon", "icon.ico")
    
    if not os.path.exists(src_path):
        print(f"Error: {src_path} not found.")
        return

    try:
        img = Image.open(src_path)
        # Resize to various standard icon sizes
        icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        
        print(f"Converting {src_path} to {dst_path} with sizes: {icon_sizes}")
        
        img.save(dst_path, format='ICO', sizes=icon_sizes)
        print("Success!")
        
    except Exception as e:
        print(f"Failed to create icon: {e}")

if __name__ == "__main__":
    create_ico()
