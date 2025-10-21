# src/utils/exception_handlers/function_handlers.py
import inspect
import asyncio
from src.utils.loggers import central_logger
from src.utils.loggers import starknet_logger
from src.utils.loggers import arduino_logger
from src.utils.async_runner import AsyncRunner  # Your custom runner


class FunctionCallHandler:
    def __init__(self, logger):
        self.logger = logger
        self._runner = None  # Lazily initialized only when needed

    def _get_runner(self):
        if self._runner is None:
            self._runner = AsyncRunner()
        return self._runner

    def call(self, fn, *args, **kwargs):
        """
        Call a sync function. Raise if coroutine function is passed.
        """
        try:
            if inspect.iscoroutinefunction(fn):
                raise TypeError("Use 'acall' or 'run' for async functions.")
            return fn(*args, **kwargs)
        except ValueError as e:
            self.logger.error(f"{e}")
        except Exception:
            self.logger.exception("Unexpected error during function call")
        return None

    async def acall(self, fn, *args, **kwargs):
        """
        Call an async function in an async context.
        """
        try:
            if not inspect.iscoroutinefunction(fn):
                raise TypeError("Use 'call' for sync functions.")
            return await fn(*args, **kwargs)
        except ValueError as e:
            self.logger.error(f"{e}")
        except Exception:
            self.logger.exception("Unexpected error during async function call")
        return None

    def run(self, fn, *args, **kwargs):
        """
        Universal runner: Detects if function is async or sync.
        Automatically runs async functions using AsyncRunner.
        """
        try:
            if inspect.iscoroutinefunction(fn):
                return self._get_runner().run_async(fn(*args, **kwargs))
            else:
                return fn(*args, **kwargs)
        except ValueError as e:
            self.logger.error(f"{e}")
        except Exception:
            self.logger.exception("Unexpected error during function call")
        return None

    def shutdown(self):
        if self._runner:
            self._runner.shutdown()

    def run_no_wait(self, fn, *args, **kwargs):
        """
        Runs an async function in the background using AsyncRunner (fire-and-forget).
        Ignores sync functions.
        """
        try:
            if not inspect.iscoroutinefunction(fn):
                self.logger.warning(f"Ignoring sync function '{fn.__name__}' in run_no_wait.")
                return None
            self._get_runner().run_async_nowait(fn(*args, **kwargs))
        except Exception:
            self.logger.exception("Unexpected error during run_no_wait")
        return None


# Central-specific instance
central_fn_handler = FunctionCallHandler(central_logger)
starknet_fn_handler = FunctionCallHandler(starknet_logger)
arduino_fn_handler = FunctionCallHandler(arduino_logger)
