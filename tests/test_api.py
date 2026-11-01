import asyncio
import io
import json
from unittest.mock import MagicMock, AsyncMock, patch

import aiohttp
import pytest

from aiotg import Bot, BotApiError


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
    loop.run_until_complete(
        bot._api_call("sendDocument", chat_id="123", document=file_obj)
    )

    args, kwargs = session.post.call_args
    assert "data" in kwargs
    assert kwargs["data"]["document"] is file_obj

    # 2. Test nested dict serialization
    nested_params = {
        "chat_id": "123",
        "reply_markup": {"inline_keyboard": [[{"text": "button"}]]},
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


def _api_response(status, body=None, headers=None, json_error=None):
    """Stand-in for aiohttp's ClientResponse, which needs a real socket."""
    resp = MagicMock()
    resp.status = status
    resp.headers = {"content-type": "application/json", **(headers or {})}
    if json_error is not None:
        resp.json = AsyncMock(side_effect=json_error)
    else:
        resp.json = AsyncMock(return_value=body)
    resp.release = AsyncMock()
    return resp


def _flood_body(retry_after):
    return {
        "ok": False,
        "error_code": 429,
        "description": f"Too Many Requests: retry after {retry_after}",
        "parameters": {"retry_after": retry_after},
    }


def _call_with_responses(responses):
    """Run one sendMessage against queued responses, with sleeping disabled.

    ``responses`` is a list, or a callable producing the next response.
    Returns (outcome, number of POSTs made, the delays the bot slept for),
    where outcome is the call's result, or the BotApiError it gave up with.
    """
    bot = Bot("token")
    session = AsyncMock()
    session.closed = False
    session.post.side_effect = responses
    bot._session = session

    with patch("aiotg.bot.asyncio.sleep", new=AsyncMock()) as sleep:
        try:
            outcome = asyncio.run(
                bot._api_call("sendMessage", chat_id="123", text="hi")
            )
        except BotApiError as err:
            outcome = err

    return outcome, session.post.call_count, [c.args[0] for c in sleep.call_args_list]


OK_BODY = {"ok": True, "result": {"message_id": 1}}


@pytest.mark.parametrize(
    "first_response, want_delay",
    [
        # Telegram's own hint, plus the 2 second safety margin
        (dict(status=429, body=_flood_body(7)), 9),
        # No hint in the body, but the HTTP header carries one
        (
            dict(
                status=429,
                body={"ok": False, "error_code": 429, "description": "Too Many"},
                headers={"Retry-After": "5"},
            ),
            7,
        ),
        # No hint anywhere: the old fixed wait
        (
            dict(
                status=429,
                body={"ok": False, "error_code": 429, "description": "Too Many"},
            ),
            30,
        ),
        # Body is not JSON at all (e.g. an HTML page from a proxy)
        (
            dict(
                status=429,
                json_error=aiohttp.ContentTypeError(MagicMock(), ()),
            ),
            30,
        ),
        # Server errors are not flood limits: fixed wait, even if a body
        # happens to carry a retry_after
        (dict(status=503, body=_flood_body(7)), 30),
    ],
    ids=["body-hint", "header-hint", "no-hint", "non-json-body", "server-error"],
)
def test_retryable_response_waits_before_retrying(first_response, want_delay):
    result, posts, delays = _call_with_responses(
        [_api_response(**first_response), _api_response(200, OK_BODY)]
    )

    assert result == OK_BODY
    assert posts == 2
    assert delays == [want_delay]


def test_flood_limit_is_retried_until_it_succeeds():
    # More 429s in a row than any small retry cap would survive, each with
    # its own hint
    floods = [_api_response(429, _flood_body(n)) for n in (1, 3, 2, 5, 4)]

    result, posts, delays = _call_with_responses(floods + [_api_response(200, OK_BODY)])

    assert result == OK_BODY
    assert posts == 6
    assert delays == [3, 5, 4, 7, 6]


def _never_recovers(status):
    """Responses that fail forever, unless the bot keeps retrying past its cap."""
    posts = 0

    def next_response(*args, **kwargs):
        nonlocal posts
        posts += 1
        if posts > 101:
            raise AssertionError("still retrying after the 100th retry")
        return _api_response(status, _flood_body(1))

    return next_response


def test_succeeds_on_the_last_allowed_retry():
    floods = [_api_response(429, _flood_body(1)) for _ in range(100)]

    result, posts, delays = _call_with_responses(floods + [_api_response(200, OK_BODY)])

    assert result == OK_BODY
    assert posts == 101
    assert delays == [3] * 100


@pytest.mark.parametrize(
    "status, want_delay",
    [(429, 3), (503, 30)],
    ids=["flood-limit", "server-error"],
)
def test_gives_up_with_an_error_after_100_retries(status, want_delay):
    result, posts, delays = _call_with_responses(_never_recovers(status))

    assert isinstance(result, BotApiError)
    assert result.response.status == status
    # The first attempt plus 100 retries, and no sleep after the last one
    assert posts == 101
    assert delays == [want_delay] * 100
