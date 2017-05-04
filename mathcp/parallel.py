import logging
import multiprocessing
from multiprocessing.pool import AsyncResult
from typing import Iterable

from mathcp.loop import Tickable

logger = logging.getLogger(__name__)


class Task(Tickable):
    """
    This is a wrapper for AsyncResult object returned by the multiprocessing pool
    to be executed in the Loop, it also holds the supplied callbacks to be called
    when task is finished.

    on_success is called when no exception is thrown by the operation
    on_error is called if operation throws an exception
    """

    def __init__(self, result: AsyncResult, on_success: callable, on_error: callable):
        super().__init__()
        self._result = result
        self._on_success = on_success
        self._on_error = on_error

    def tick(self) -> None:
        if self._result.ready():
            try:
                self._on_success(self._result.get())
                logger.info("Task successful")
            except Exception as e:
                self._on_error(e)
                logger.info("Task error")

            self.destroy()

    def destroy(self) -> None:
        super().destroy()
        del self._result
        del self._on_success
        del self._on_error

    def __del__(self) -> None:
        logger.debug("Destruct %s", type(self))


class Pool(Tickable):
    """
    This is a multiprocessing pool wrapper to offload a CPU intensive tasks to a pool of subprocess
    so they don't load the main server loop.
    """

    def __init__(self):
        super().__init__()
        self._pool = multiprocessing.Pool()

    def add(self, func: callable, args: Iterable, on_success: callable, on_error: callable) -> None:
        task = Task(self._pool.apply_async(func, args=args), on_success, on_error)
        self.loop.add(task)

    def __del__(self) -> None:
        logger.debug("Destruct %s", type(self))
