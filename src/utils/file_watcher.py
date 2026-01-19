import os
import time
from typing import Callable
from watchdog.events import FileSystemEventHandler

class FileWatcher(FileSystemEventHandler):
    """File change monitoring class"""
    
    def __init__(self, callback: Callable[[], None], file_path: str):
        self.callback = callback
        # Normalize path
        self.file_path = os.path.normpath(os.path.abspath(file_path))
        self.last_modified = 0.0
    
    def on_modified(self, event):
        if not event.is_directory:
            # Normalize event path for comparison
            try:
                event_path = os.path.normpath(os.path.abspath(event.src_path))
                
                is_target = False
                if os.path.exists(event_path) and os.path.exists(self.file_path):
                    try:
                        is_target = os.path.samefile(event_path, self.file_path)
                    except Exception:
                        # Fallback if samefile fails (e.g. different drives or permissions)
                        is_target = event_path.lower() == self.file_path.lower()
                else:
                    # Fallback for deleted files or other edge cases
                    is_target = event_path.lower() == self.file_path.lower()

                if is_target:
                    # Prevent duplicate events in short timeframe
                    current_time = time.time()
                    if current_time - self.last_modified > 1.0:
                        self.last_modified = current_time
                        print(f"File change detected: {event_path}")
                        self.callback()
            except Exception as e:
                print(f"FileWatcher check error: {e}")
