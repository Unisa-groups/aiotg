import asyncio
from collections.abc import Awaitable
from typing import Any, override

from .bot import Bot


class MockBot(Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__("test_token", *args, **kwargs)
        self.calls: dict[str, Any] = {}

    @override
    def api_call(self, method: str, **params: Any) -> Awaitable[Any]:
        self.calls[method] = params
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result("1")
        return future
