"""
Background task execution system for Agent Zero.

This module provides a clean async-based background task execution system
to replace DeferredTask for settings updates and other background operations.
"""

import asyncio
import threading
from typing import Any, Callable, Coroutine, Optional, TypeVar
from concurrent.futures import Future
from python.helpers.print_style import PrintStyle

T = TypeVar("T")


class BackgroundTaskManager:
    """
    Singleton manager for executing background tasks.

    Uses a dedicated event loop thread for running async operations
    without blocking the main thread.
    """

    _instance: Optional["BackgroundTaskManager"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "BackgroundTaskManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self._initialized = True
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._tasks: dict[str, Future] = {}
        self._start_loop()

    def _start_loop(self) -> None:
        """Start the background event loop in a dedicated thread."""
        if self._loop is not None and self._loop.is_running():
            return

        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name="BackgroundTasks"
        )
        self._thread.start()

    def _run_loop(self) -> None:
        """Run the event loop forever."""
        if self._loop:
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()

    def run_task(
        self,
        coro_func: Callable[..., Coroutine[Any, Any, T]],
        *args: Any,
        task_id: Optional[str] = None,
        **kwargs: Any
    ) -> Future[T]:
        """
        Run an async function in the background.

        Args:
            coro_func: Async function to execute
            *args: Positional arguments for the function
            task_id: Optional identifier for the task
            **kwargs: Keyword arguments for the function

        Returns:
            Future that can be awaited or checked for completion
        """
        self._start_loop()

        if not self._loop:
            raise RuntimeError("Background event loop not initialized")

        async def wrapper() -> T:
            try:
                return await coro_func(*args, **kwargs)
            except Exception as e:
                PrintStyle(
                    background_color="red",
                    font_color="white",
                    padding=True
                ).print(f"Background task error: {type(e).__name__}: {e}")
                raise

        future = asyncio.run_coroutine_threadsafe(wrapper(), self._loop)

        if task_id:
            # Cancel any existing task with the same ID
            if task_id in self._tasks:
                old_future = self._tasks[task_id]
                if not old_future.done():
                    old_future.cancel()
            self._tasks[task_id] = future

        return future

    def run_sync(
        self,
        func: Callable[..., T],
        *args: Any,
        task_id: Optional[str] = None,
        **kwargs: Any
    ) -> Future[T]:
        """
        Run a synchronous function in the background thread.

        Args:
            func: Sync function to execute
            *args: Positional arguments for the function
            task_id: Optional identifier for the task
            **kwargs: Keyword arguments for the function

        Returns:
            Future that can be awaited or checked for completion
        """
        async def async_wrapper() -> T:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

        return self.run_task(async_wrapper, task_id=task_id)

    def is_task_running(self, task_id: str) -> bool:
        """Check if a task with the given ID is currently running."""
        if task_id in self._tasks:
            return not self._tasks[task_id].done()
        return False

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task by ID."""
        if task_id in self._tasks:
            future = self._tasks[task_id]
            if not future.done():
                future.cancel()
                return True
        return False

    def shutdown(self) -> None:
        """Shutdown the background task manager."""
        # Cancel all pending tasks
        for future in self._tasks.values():
            if not future.done():
                future.cancel()
        self._tasks.clear()

        # Stop the event loop
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

        # Wait for thread to finish
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)

        self._loop = None
        self._thread = None


# Global instance for easy access
_manager: Optional[BackgroundTaskManager] = None


def get_manager() -> BackgroundTaskManager:
    """Get the global background task manager instance."""
    global _manager
    if _manager is None:
        _manager = BackgroundTaskManager()
    return _manager


def run_background(
    coro_func: Callable[..., Coroutine[Any, Any, T]],
    *args: Any,
    task_id: Optional[str] = None,
    **kwargs: Any
) -> Future[T]:
    """
    Convenience function to run an async function in the background.

    Args:
        coro_func: Async function to execute
        *args: Positional arguments for the function
        task_id: Optional identifier for the task
        **kwargs: Keyword arguments for the function

    Returns:
        Future that can be awaited or checked for completion
    """
    return get_manager().run_task(coro_func, *args, task_id=task_id, **kwargs)


def run_background_sync(
    func: Callable[..., T],
    *args: Any,
    task_id: Optional[str] = None,
    **kwargs: Any
) -> Future[T]:
    """
    Convenience function to run a sync function in the background.

    Args:
        func: Sync function to execute
        *args: Positional arguments for the function
        task_id: Optional identifier for the task
        **kwargs: Keyword arguments for the function

    Returns:
        Future that can be awaited or checked for completion
    """
    return get_manager().run_sync(func, *args, task_id=task_id, **kwargs)
