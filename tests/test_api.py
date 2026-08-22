
import asyncio
import io
import json
from unittest.mock import MagicMock, AsyncMock
import aiohttp
import pytest
from aiotg import Bot

def test_api_call_preprocessing():
    bot = Bot("token")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Mock aiohttp session
    session = AsyncMock()
    session.closed = False
    bot._session = session
    
    # Successful response mock
    resp_ok = MagicMock()
    resp_ok.status = 200
    resp_ok.json = AsyncMock(return_value={"ok": True, "result": {}})
    resp_ok.headers = {"content-type": "application/json"}
    resp_ok.release = AsyncMock()
    session.post.return_value = resp_ok
    
    # 1. Test file upload
    file_obj = io.BytesIO(b"hello")
    loop.run_until_complete(bot._api_call("sendDocument", chat_id="123", document=file_obj))
    
    args, kwargs = session.post.call_args
    assert "data" in kwargs
    assert kwargs["data"]["document"] is file_obj
    
    # 2. Test nested dict serialization
    nested_params = {
        "chat_id": "123",
        "reply_markup": {"inline_keyboard": [[{"text": "button"}]]}
    }
    session.post.reset_mock()
    loop.run_until_complete(bot._api_call("sendMessage", **nested_params))
    
    args, kwargs = session.post.call_args
    assert "data" in kwargs
    data = kwargs["data"]
    assert isinstance(data["reply_markup"], str)
    assert json.loads(data["reply_markup"]) == nested_params["reply_markup"]

    loop.run_until_complete(bot.session.close())
    loop.close()
