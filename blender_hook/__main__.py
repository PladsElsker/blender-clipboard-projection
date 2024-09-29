import sys
sys.path[0:0] = ['.']

from threading import Thread

from blender_hook.watcher import Watcher, ChangeEvent
from blender_hook.zip import zip_directory
from blender_hook.export import export_directory
from blender_hook.config import config


def start_hook():
    watcher_thread = Thread(
        target=Watcher(
            config['Watch'], 
            [
                LogChanges(),
                ZipProject(),
                ExportDirectory(),
            ]
        ).run,
    )
    watcher_thread.start()
    print(f'Started blender hook')
    watcher_thread.join()


class ZipProject(ChangeEvent):
    def handle(self, root):
        zip_directory(root, f'{config["Watch"]}.zip', ignored=['__pycache__'])


class ExportDirectory(ChangeEvent):
    def handle(self, root):
        export_directory(root, config['Addon'], siblings=['addon', 'assets', 'commotion'])


class LogChanges(ChangeEvent):
    def handle(self, root):
        print(f"Changes detected")


start_hook()
