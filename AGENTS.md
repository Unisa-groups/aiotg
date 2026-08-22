# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Commands

Environment is managed with `hatch` (env config in `pyproject.toml`); `uv.lock` is also present.

- Test all: `hatch run test:pytest` (or plain `pytest` inside the venv)
- Test single file: `pytest tests/test_callbacks.py`
- Test single case: `pytest tests/test_callbacks.py::test_name` or `pytest -k pattern`
- Lint (flake8 + black --check): `hatch run lint:style`
- Format: `hatch run lint:fmt`
- Full lint suite (used in CI): `hatch run lint:all`

## Architecture

Small single-package library (`aiotg/`) wrapping the Telegram Bot API with asyncio.

- **`bot.py`** — `Bot` is the core object. Handlers are registered via decorators (`command`, `default`, `inline`, `chosen_inline_result_callback`, `callback`, `checkout`, `handle`), each appending `(regexp, fn)` pairs to a list on the instance. `run()` starts a long-polling loop (`getUpdates`); `run_webhook()` starts an aiohttp `web.Application` instead. Every incoming update — polled or via webhook — passes through `_process_update`, which dispatches by update type (message-like via `MESSAGE_UPDATES`, `inline_query`, `callback_query`, `pre_checkout_query`, `chosen_inline_result`, else `_process_not_handled_update`) and schedules the resulting coroutine with `asyncio.ensure_future`. Outbound Telegram API calls all funnel through `Bot.api_call`, which handles retries on `RETRY_CODES`.
- **`chat.py`** — `Chat`/`Sender` represent a conversation; all outbound message methods (`send_text`, `reply`, `send_photo`, `send_media_group`, etc.) live here and call back into `bot.api_call`.
- **`types_.py`** — `TypedDict` definitions mirroring the Telegram Bot API JSON schemas (`TG_Message`, `TG_Update`, `TG_Chat`, ...). Purely for static typing/editor completion — there is no runtime validation against these.
- **`mock.py`** — `MockBot` subclasses `Bot` and overrides `api_call` to record calls instead of hitting the network. This is the standard way tests exercise the bot (see `tests/test_callbacks.py`).
- **`reloader.py`** — dev-only auto-reload (via `watchdog`), wired in through `bot.run(reload=True)`.

Handler matching is regex-based and order-dependent: within a handler kind, registered `(regexp, fn)` pairs are tried in registration order until one matches.
