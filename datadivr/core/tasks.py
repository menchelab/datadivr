import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from functools import wraps
from typing import Any, ClassVar, ParamSpec, TypeVar

from datadivr.utils.logging import get_logger

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")


logger = get_logger(__name__)


class BackgroundTasks:
    _tasks: ClassVar[dict[str, tuple[Callable[[], Awaitable[Any]], float]]] = {}
    _running_tasks: ClassVar[set[asyncio.Task[Any]]] = set()

    @classmethod
    def task(
        cls, name: str | None = None
    ) -> Callable[[Callable[P, Coroutine[Any, Any, T]]], Callable[P, Coroutine[Any, Any, T]]]:
        """Decorator to register a one-off task."""

        def decorator(func: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, Coroutine[Any, Any, T]]:
            @wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                task_name = name or func.__name__
                try:
                    task: asyncio.Task[T] = asyncio.create_task(func(*args, **kwargs))
                    cls._running_tasks.add(task)
                    logger.debug(f"Task started: {task_name}")
                    return await task
                finally:
                    cls._running_tasks.discard(task)
                    logger.debug(f"Task completed: {task_name}")

            return wrapper

        return decorator

    @classmethod
    def periodic(
        cls, interval: float, name: str | None = None
    ) -> Callable[[Callable[[], Coroutine[Any, Any, Any]]], Callable[[], Coroutine[Any, Any, Any]]]:
        """Decorator to register a periodic background task."""

        def decorator(func: Callable[[], Coroutine[Any, Any, Any]]) -> Callable[[], Coroutine[Any, Any, Any]]:
            task_name = name or func.__name__
            cls._tasks[task_name] = (func, interval)

            @wraps(func)
            async def wrapper() -> Any:
                return await func()

            return wrapper

        return decorator

    @classmethod
    async def start_all(cls) -> None:
        """Start all registered periodic tasks."""
        for name, (func, interval) in cls._tasks.items():
            cls._running_tasks.add(asyncio.create_task(cls._run_periodic(func, interval, name)))
            logger.info(f"Started periodic task: {name}")

    @classmethod
    async def stop_all(cls) -> None:
        """Stop all running tasks."""
        for task in cls._running_tasks:
            task.cancel()
        if cls._running_tasks:
            await asyncio.gather(*cls._running_tasks, return_exceptions=True)
        cls._running_tasks.clear()
        logger.info("All tasks stopped")

    @staticmethod
    async def _run_periodic(func: Callable[[], Awaitable[Any]], interval: float, name: str) -> None:
        """Run a periodic task at the specified interval."""
        while True:
            try:
                await func()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                logger.info(f"Task cancelled: {name}")
                raise
            except Exception:
                logger.exception(f"Error in task {name}")
                await asyncio.sleep(interval)
