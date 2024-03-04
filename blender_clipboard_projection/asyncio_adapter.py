import bpy
import asyncio
import functools


class AsyncioBlenderAdapter:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.active_run_function = None

    def _run_asyncio_loop(self, *, every):
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()
        return every

    def start(self, every=0.1):
        if not self.active_run_function:
            self.active_run_function = functools.partial(self._run_asyncio_loop, every=every)
            bpy.app.timers.register(self.active_run_function)

    def stop(self):
        if self.active_run_function:
            bpy.app.timers.unregister(self.active_run_function)
            self.active_run_function = None


asyncio_adapter = AsyncioBlenderAdapter()
