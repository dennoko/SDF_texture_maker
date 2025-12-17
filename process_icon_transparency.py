from PIL import Image
import collections

def process_icon():
    src = "icon/icon_backup.png"
    dst_png = "icon/icon.png"
    dst_ico = "icon/icon.ico"
    
    print(f"Opening {src}...")
    try:
        img = Image.open(src).convert("RGBA")
    except FileNotFoundError:
        print("Error: icon_backup.png not found!")
        return

    width, height = img.size
    pixels = img.load()
    
    # BFS Flood Fill from corners
    # Identify "white-ish" background pixels and turn them transparent
    
    # Starting points: 4 corners
    queue = collections.deque([(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)])
    visited = set(queue)
    
    print("Processing transparency...")
    count = 0
    while queue:
        x, y = queue.popleft()
        
        # Check bounds (already checked before adding, but safe to double check)
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
            
        r, g, b, a = pixels[x, y]
        
        # Check if pixel is in the "white" range [245, 255]
        # and not already transparent (optimization)
        if a > 0 and r >= 245 and g >= 245 and b >= 245:
            # Make transparent
            pixels[x, y] = (0, 0, 0, 0)
            count += 1
            
            # Add neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
    
    print(f"Processed {count} pixels.")
    
    print(f"Saving to {dst_png}...")
    img.save(dst_png)
    
    print(f"Saving to {dst_ico}...")
    img.save(dst_ico, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("Done.")

if __name__ == "__main__":
    process_icon()
