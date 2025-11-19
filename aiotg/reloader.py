import asyncio
import os
import sys
from os.path import realpath
from typing import Any, Callable, Never, override

from watchdog.events import FileSystemEvent as Event
from watchdog.events import PatternMatchingEventHandler as EventHandler
from watchdog.observers import Observer


# Event handler class for watchdog
class Handler(EventHandler):
    # Private
    _future_resolved: bool = False

    def __init__(
        self, loop: asyncio.AbstractEventLoop, *args: Any, **kwargs: Any
    ) -> None:
        self.loop: asyncio.AbstractEventLoop = loop

        # awaitable future to race on
        self.changed: asyncio.Future[Event] = asyncio.Future(loop=loop)

        # Set default patterns if not provided by the caller, then initialize
        # the parent class.
        kwargs.setdefault(
            "patterns",
            ["*.py", "*.txt", "*.aiml", "*.json", "*.cfg", "*.xml", "*.html"],
        )

        # Continue init for EventHandler
        super().__init__(*args, **kwargs)

    @override
    def on_any_event(self, event: Event):
        # Resolve future
        if isinstance(event, Event) and not self._future_resolved:
            self.loop.call_soon_threadsafe(self.changed.set_result, event)
            self._future_resolved = True


def clear_screen() -> None:
    if os.name == "nt":
        seq = "\x1bc"
    else:
        seq = "\x1b[2J\x1b[H"

    sys.stdout.write(seq)


def reload() -> Never:
    """Reload process"""
    try:
        # Reload and replace current process
        os.execv(sys.executable, [sys.executable] + sys.argv)

    except OSError:
        # Ugh, that failed
        # Try spawning a new process and exitj
        os.spawnv(os.P_NOWAIT, sys.executable, [sys.executable] + sys.argv)
        os._exit(os.EX_OK)


async def run_with_reloader(
    loop: asyncio.AbstractEventLoop,
    coroutine: asyncio.Task[Any],
    cleanup: Callable[[], Any] | None = None,
) -> None:
    """Run coroutine with reloader"""

    clear_screen()
    print("🤖  Running in debug mode with live reloading")
    print("    (don't forget to disable it for production)")

    # Create watcher
    handler = Handler(loop)
    watcher = Observer()

    # Setup
    path = realpath(os.getcwd())
    watcher.schedule(handler, path=path, recursive=True)
    watcher.start()

    print("    (watching {})".format(path))

    # Run watcher and coroutine together
    done, pending = await asyncio.wait(
        [coroutine, handler.changed], return_when=asyncio.FIRST_COMPLETED
    )

    # Cleanup
    if cleanup:
        cleanup()
    watcher.stop()

    for fut in done:
        # If change event, then reload
        if isinstance(fut.result(), Event):
            print("Reloading...")
            reload()
