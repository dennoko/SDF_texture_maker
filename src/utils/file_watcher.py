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
            event_path = os.path.normpath(os.path.abspath(event.src_path))
            if event_path == self.file_path:
                # Prevent duplicate events in short timeframe
                current_time = time.time()
                if current_time - self.last_modified > 1.0:
                    self.last_modified = current_time
                    self.callback()
