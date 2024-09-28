import os
import time
import zipfile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Watcher:
    DIRECTORY_TO_WATCH = "./blender_clipboard_projection"
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
        print(f"Changes detected: {event.src_path}")
        zip_directory(Watcher.DIRECTORY_TO_WATCH, Watcher.ZIP_FILE_NAME)


def zip_directory(folder_path, zip_path):
    if os.path.exists(zip_path) and os.path.isfile(zip_path):
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(
                    file_path,
                    file_path
                )

if __name__ == "__main__":
    print(f'Starting watcher on {Watcher.DIRECTORY_TO_WATCH}/')
    w = Watcher()
    w.run()
