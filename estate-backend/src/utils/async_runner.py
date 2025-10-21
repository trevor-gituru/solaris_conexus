# src/utils/async_runner.py

import asyncio
import threading

class AsyncRunner:
    """
    Runs async functions from sync code using a dedicated background event loop thread.
    Tracks running tasks for graceful shutdown.
    """

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._start_loop, daemon=True)
        self._tasks = set()
        self._loop_running = threading.Event()
        self._thread.start()
        self._loop_running.wait()

    def _start_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop_running.set()
        self._loop.run_forever()

    def run_async(self, coro):
        """
        Run an async function and return its result (blocking).
        """
        if not self._loop.is_running():
            raise RuntimeError("AsyncRunner loop is not running.")
        future = asyncio.run_coroutine_threadsafe(self._track_task(coro), self._loop)
        try:
            return future.result()
        finally:
            self._tasks.discard(future)

    def run_async_nowait(self, coro):
        """
        Run an async function without waiting (non-blocking).
        """
        if not self._loop.is_running():
            raise RuntimeError("AsyncRunner loop is not running.")
        task = asyncio.run_coroutine_threadsafe(self._track_task(coro), self._loop)

    async def _track_task(self, coro):
        task = asyncio.current_task()
        self._tasks.add(task)
        try:
            return await coro
        finally:
            self._tasks.discard(task)

    def shutdown(self):
        """
        Cancel all running tasks and shut down the event loop.
        """
        for task in list(self._tasks):
            task.cancel()

        def stop_loop():
            self._loop.stop()

        self._loop.call_soon_threadsafe(stop_loop)
        self._thread.join()
