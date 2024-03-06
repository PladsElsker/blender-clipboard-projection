import os
import time
import zipfile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:
    DIRECTORY_TO_WATCH = "./"
    ZIP_FILE_NAME = "blender_clipboard_projection.zip"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_modified(event):
        if event.is_directory:
            return None
        if Watcher.ZIP_FILE_NAME in event.src_path:
            return None
        if "watch_zip.py" in event.src_path:
            return None
        if ".venv" in event.src_path:
            return None
        if ".git" in event.src_path:
            return None

        print(f"Change detected: {event.src_path}")
        zip_directory(Watcher.DIRECTORY_TO_WATCH, Watcher.ZIP_FILE_NAME, exclude_dir=[".venv", ".git"])


def zip_directory(folder_path, zip_path, exclude_dir=None):
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            if exclude_dir:
                dirs[:] = [d for d in dirs if d not in exclude_dir]
            for file in files:
                file_path = os.path.join(root, file)
                if exclude_dir and f"/{exclude_dir}/" in file_path:
                    continue
                zipf.write(file_path, 
                           os.path.relpath(file_path, 
                                           folder_path))

if __name__ == "__main__":
    w = Watcher()
    w.run()
