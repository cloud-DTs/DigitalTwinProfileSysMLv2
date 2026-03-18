"""
Internal GC interface. Currently only Documents are collected by the internal garbage collector.
"""

from typing import overload

from ... import core


class Debug:
    """Debug options for the garbage collector."""

    def __init__(self, stats: bool = False, collected: bool = False, reachable: bool = False, unreachable: bool = False) -> None: ...

    @property
    def stats(self) -> bool:
        """Print statistics summary during collection."""

    @stats.setter
    def stats(self, arg: bool, /) -> None: ...

    @property
    def collected(self) -> bool:
        """Print collected documents during collection."""

    @collected.setter
    def collected(self, arg: bool, /) -> None: ...

    @property
    def reachable(self) -> bool:
        """Print reachable documents during collection."""

    @reachable.setter
    def reachable(self, arg: bool, /) -> None: ...

    @property
    def unreachable(self) -> bool:
        """Print unreachable documents during collection."""

    @unreachable.setter
    def unreachable(self, arg: bool, /) -> None: ...

def collect() -> None:
    """Explicitly call garbage collector once."""

def disable() -> None:
    """Disable automatic garbage collection."""

def enable() -> None:
    """Enable automatic garbage collection."""

def get_count() -> int:
    """Returns the number of currently tracked objects."""

def get_debug() -> Debug:
    """Return a copy of the current debug options of the garbage collector."""

def get_executor() -> core.Executor | None:
    """The executor assigned to the garbage collector."""

def get_threshold() -> int:
    """Return the current threshold."""

@overload
def is_tracked(arg: core.SharedMutex[core.BasicDocument], /) -> bool:
    """Returns ``True`` if ``document`` is tracked by the garbage collector."""

@overload
def is_tracked(arg: core.BasicDocument, /) -> bool: ...

def isenabled() -> bool:
    """Returns ``True`` if automatic collection is enabled."""

def set_debug(arg: Debug, /) -> None:
    """
    Set default options for the garbage collector. By default, everything is printed to stderr.
    """

def set_executor(arg: core.Executor, /) -> None:
    """
    Assign an executor to the garbage collector. Without an executor, the garbage collector always runs on the thread that invokes it, e.g. the main thread. In addition to processing documents concurrently, documents will also be destroyed asynchronously further improving performance.
    """

def set_threshold(arg: int, /) -> None:
    """
    Set the garbage collector threshold, 0 disables collection. Negative values raise ``ValueError``.

    Garbage collector will automatically run only when it tracks more than *threshold* new objects since last collection.
    """

def track(arg: core.SharedMutex[core.BasicDocument], /) -> bool:
    """
    Add document to garbage collector tracking list. Returns ``False`` if document was already tracked.
    """

@overload
def untrack(arg: core.SharedMutex[core.BasicDocument], /) -> bool:
    """
    Remove document from the garbage collector tracking list. Returns ``False`` if document was not tracked.
    """

@overload
def untrack(arg: core.BasicDocument, /) -> bool: ...

