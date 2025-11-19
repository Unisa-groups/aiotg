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
        future: asyncio.Future[Any] = asyncio.Future()
        future.set_result("1")
        return future
