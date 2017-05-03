import logging
import multiprocessing
from multiprocessing.pool import AsyncResult
from typing import Iterable

from mathcp.loop import Tickable

logger = logging.getLogger(__name__)


class Task(Tickable):
    def __init__(self, result: AsyncResult, on_success: callable, on_error: callable):
        super().__init__()
        self.result = result
        self.on_success = on_success
        self.on_error = on_error

    def tick(self):
        if self.result.ready():
            try:
                self.on_success(self.result.get())
                logger.info("Task successful")
            except Exception as e:
                self.on_error(e)
                logger.info("Task error")

            self.destroy()

    def destroy(self):
        super().destroy()
        del self.result
        del self.on_success
        del self.on_error

    def __del__(self):
        logger.debug("Destruct %s", type(self))


class Pool(Tickable):
    def __init__(self):
        super().__init__()
        self._pool = multiprocessing.Pool()

    def add(self, func: callable, args: Iterable, on_success: callable, on_error: callable):
        task = Task(self._pool.apply_async(func, args=args), on_success, on_error)
        self.loop.add(task)

    def __del__(self):
        logger.debug("Destruct %s", type(self))