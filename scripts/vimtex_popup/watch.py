from pathlib import Path
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def __init__(self, name, callback, final_callback, observer) -> None:
        super().__init__()
        self.name = name
        self.callback = callback
        self.final_callback = final_callback
        self.observer = observer
    def on_any_event(self, event):
        print(event.event_type, event.src_path)
    
        if event.is_directory:
            return None
        # :w
        elif event.event_type == 'modified' and event.src_path.endswith(self.name):
            self.callback()
        # :wq
        elif event.event_type == 'deleted' and event.src_path.endswith(f'.{self.name}.swp'):
            self.observer.stop()
            self.final_callback()
            

            

def watch(path:Path, callback, final_callback):
    watching_folder = path.parent
    name = path.name
    observer = Observer()
    observer.schedule(MyHandler(name, callback, final_callback, observer), watching_folder, recursive=False)
    observer.start()
    
    observer.join()



if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s - %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()