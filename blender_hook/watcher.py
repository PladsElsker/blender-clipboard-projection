import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from blender_hook.debounce import Debouncer


class Watcher:
    def __init__(self, directory, events):
        self.observer = Observer()
        self.directory = directory
        self.events = events

    def run(self):
        event_handler = Handler(self)
        self.observer.schedule(event_handler, self.directory, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()


class Handler(FileSystemEventHandler):
    def __init__(self, watcher):
        self.watcher = watcher
        self.handle = Debouncer(1, self._handle)
    
    def _handle(self, event):
        [e.handle(self.watcher.directory) for e in self.watcher.events if isinstance(e, ChangeEvent)]

    def on_modified(self, event):
        self.handle.call(event)

    def on_created(self, event):
        self.handle.call(event)

    def on_deleted(self, event):
        self.handle.call(event)
    

class ChangeEvent:
    def handle(self, root):
        raise NotImplementedError()
