import threading


class Debouncer:
    def __init__(self, wait_time, func):
        self.wait_time = wait_time
        self.func = func
        self.timer = None

    def call(self, *args, **kwargs):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.wait_time, self.func, args=args, kwargs=kwargs)
        self.timer.start()

    def cancel(self):
        if self.timer:
            self.timer.cancel()
