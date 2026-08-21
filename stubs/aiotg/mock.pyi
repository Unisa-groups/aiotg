from .bot import Bot as Bot
from collections.abc import Awaitable
from typing import Any, override

class MockBot(Bot):
    calls: dict[str, Any]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    @override
    def api_call(self, method: str, **params: Any) -> Awaitable[Any]: ...
