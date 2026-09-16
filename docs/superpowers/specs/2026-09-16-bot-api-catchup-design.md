# Telegram Bot API catch-up — Phase 1: core method coverage

**Status:** approved for spec review
**Date:** 2026-09-16

## Summary

`aiotg` wraps the Telegram Bot API with asyncio. Its type definitions
(`aiotg/types_.py`) were updated relatively recently and already model
fields through roughly Bot API 9.2/9.3 (gifts, checklists, paid messages,
business-connection fields). The callable methods (`aiotg/bot.py`,
`aiotg/chat.py`) were not kept in sync and are missing most of the API
surface, including methods that predate all of that — chat administration,
forum topics, sticker-set management, bot profile/commands, and several
message-editing/copy/forward variants.

This phase adds that missing "core" surface: the stable, broadly-used
methods every general-purpose bot framework should expose, using the
patterns already established in the codebase. It also fixes two existing
methods that call Telegram API method names which have been renamed and
are no longer documented at all (`kickChatMember`, `getChatMembersCount`).

Telegram's live API is currently at Bot API 10.3 (August 2026) and has
shipped several large, very new subsystems since the version this library's
types track (Rich Messages, Ephemeral messages, Guest mode, Managed bots,
Community chats, Suggested Posts). Those are explicitly out of scope here —
see Non-goals.

## Motivation

- Confirmed via the live API reference (`https://core.telegram.org/bots/api`)
  that `kickChatMember` and `getChatMembersCount` no longer appear on the
  page at all — they were renamed to `banChatMember` and
  `getChatMemberCount` years ago. `aiotg`'s `Chat.kick_chat_member` and
  `Chat.get_chat_members_count` (`aiotg/chat.py`) still call the old names,
  so these two currently-advertised methods are likely already broken
  against the live API.
- Whole categories of well-established, stable API methods were never
  implemented, meaning users currently have to fall back to
  `bot.api_call("methodName", ...)` directly for anything beyond sending
  basic message types and doing simple chat lookups.
- Several update types are already represented in `TG_Update`
  (`aiotg/types_.py`) but have no dispatch path in
  `Bot._process_update` (`aiotg/bot.py`) — they silently fall through to
  `_process_not_handled_update`, which is logged as an error today. The
  types exist; the routing doesn't.

## Non-goals (explicitly out of scope for this phase)

- **Payments** (`send_invoice`, `create_invoice_link`, `answer_web_app_query`,
  the `shipping_query` handler/`ShippingQuery` class, and the associated
  `TG_Invoice`/`TG_OrderInfo`/`TG_ShippingQuery` type completions). Cut
  during design review — a future phase if/when needed.
- **Games** (`send_game`, `set_game_score`, `get_game_high_scores`,
  `TG_Game` completion). Cut during design review — Bot API's legacy
  gaming-platform integration, low usage.
- **Phase 2** (Stars transaction/refund methods, business-connection
  acting-on-behalf-of methods, gifts, checklists) — types already stubbed
  as `Any`; deliberately deferred to its own spec.
- **Phase 3** (Rich Messages, Ephemeral messages, Guest mode, Managed
  bots, Community chats, Suggested Posts) — large, very new (some shipped
  weeks before this spec), deferred to its own spec once the design is
  clearer and adoption is better understood.
- Any new file/module structure. The existing five-file layout
  (`bot.py`/`chat.py`/`types_.py`/`mock.py`/`reloader.py`) already
  separates concerns adequately; these additions are uniform, repetitive
  thin wrappers grouped by comment headers within the existing files, the
  same way `MESSAGE_TYPES`/`MESSAGE_UPDATES` already group things.
- Any validation/guarding beyond what the existing methods do (e.g. no
  `chat.is_group()` pre-checks on admin methods) — let the Telegram API
  return its own errors, consistent with current style.

## Design

### 1. Outbound methods

All new methods follow the existing thin-wrapper pattern exactly: build
the Telegram API method name, forward `chat_id`/other required positional
args plus `**options: Unpack[TG_XxxOpts]`, return
`self.bot.api_call(...)` (from `Chat`) or `self.api_call(...)` (from
`Bot`). Placement mirrors the existing rule already visible in the
codebase: methods that act on one specific chat go on `Chat` (like
`kick_chat_member`, `get_chat_administrators` today); methods that aren't
tied to an open chat go on `Bot` (like `get_me`, `leave_chat` today).

**Chat administration** (`Chat`):
`ban_chat_member`, `restrict_chat_member`, `promote_chat_member`,
`set_chat_administrator_custom_title`, `ban_chat_sender_chat`,
`unban_chat_sender_chat`, `set_chat_permissions`,
`export_chat_invite_link`, `create_chat_invite_link`,
`edit_chat_invite_link`, `revoke_chat_invite_link`,
`approve_chat_join_request`, `decline_chat_join_request`,
`set_chat_photo`, `delete_chat_photo`, `set_chat_title`,
`set_chat_description`, `pin_chat_message`, `unpin_chat_message`,
`unpin_all_chat_messages`, `get_chat_member_count`.

Corresponding `TG_*Opts` types already exist for some of these in
`types_.py` (`TG_BanChatMemberOpts`, `TG_UnbanChatMemberOpts`,
`TG_RestrictChatMemberOpts`, `TG_PromoteChatMemberOpts`,
`TG_CreateChatInviteLinkOpts`, `TG_SetChatPermissionsOpts`) — defined but
currently unused by any method. Wire these up rather than redefining them.

**Forum topics** (`Chat`, all take `chat_id`):
`create_forum_topic` (an unused `TG_CreateForumTopicOpts` +
`TG_CreateForumTopicResponse` already exist — wire up), `edit_forum_topic`,
`close_forum_topic`, `reopen_forum_topic`, `delete_forum_topic`,
`unpin_all_forum_topic_messages`, `edit_general_forum_topic`,
`close_general_forum_topic`, `reopen_general_forum_topic`,
`hide_general_forum_topic`, `unhide_general_forum_topic`,
`unpin_all_general_forum_topic_messages`.

**Bot profile & commands** (`Bot`, global or optional-scope, not
required-chat_id):
`set_my_commands`, `get_my_commands`, `delete_my_commands`, `set_my_name`,
`get_my_name`, `set_my_description`, `get_my_description`,
`set_my_short_description`, `get_my_short_description`,
`set_chat_menu_button`, `get_chat_menu_button`,
`set_my_default_administrator_rights`,
`get_my_default_administrator_rights`, `get_forum_topic_icon_stickers`.

**Stickers** (`Bot` — sticker sets aren't tied to a chat):
`get_sticker_set`, `get_custom_emoji_stickers`, `upload_sticker_file`,
`create_new_sticker_set`, `add_sticker_to_set`,
`delete_sticker_from_set`, `set_sticker_position_in_set`,
`replace_sticker_in_set`, `set_sticker_emoji_list`,
`set_sticker_keywords`, `set_sticker_mask_position`,
`set_sticker_set_title`, `set_sticker_set_thumbnail`,
`set_custom_emoji_sticker_set_thumbnail`, `delete_sticker_set`.

**Messaging completeness** (`Chat`):
`send_poll`, `send_dice`, `send_animation`, `send_video_note`,
`stop_poll`, `edit_message_live_location`, `stop_message_live_location`,
`edit_message_caption`, `edit_message_media`, `copy_message`,
`copy_messages`, `forward_messages`, `delete_messages`,
`set_message_reaction`.

`forward_message` (singular, already implemented) should also be upgraded
to accept `**options: Unpack[TG_ForwardMessageOpts]` — that type already
exists in `types_.py` and is currently unused by any method.

**Misc** (`Bot`): `get_webhook_info`, `close`, `log_out`. Note:
`close` is Telegram's `close` method (used before switching a running bot
to a different local server instance) — distinct from closing the
`aiohttp` session (`Bot.session`/`loop.run_until_complete(self.session.close())`
in `bot.py`). Keep the mechanical snake_case name for consistency with
every other method in the library, but give it a docstring that's explicit
about what it does so it isn't mistaken for session cleanup.

### 2. Inbound update handlers

Add a handler decorator, in `Bot`, for each update type that is already a
key in `TG_Update` but has no dispatch branch in `_process_update` today:
`poll`, `poll_answer`, `my_chat_member`, `chat_member`,
`chat_join_request`, `chat_boost`, `removed_chat_boost`,
`message_reaction`, `message_reaction_count`.

Each follows the simplest existing pattern in the codebase — the single
settable callback used by `default()`/`not_handled_update()` (e.g.
`self._default_poll = callback`) — not the regex dual-mode `_register()`
machinery used by `inline`/`callback`/`checkout`, since none of these
update types carry a string payload worth regex-matching against. Each
handler receives the raw typed dict for that update
(`TG_ChatMemberUpdated`, `TG_ChatJoinRequest`, etc.) directly, the same
way `handle("photo")` today receives the raw `photo` sub-dict rather than
a wrapper class.

`_process_update`'s dispatch chain (`aiotg/bot.py`) gets one `elif`
branch per new type, following the existing `if/elif` chain for
`inline_query`/`callback_query`/etc.

### 3. `MESSAGE_TYPES` additions

`MESSAGE_TYPES` (`aiotg/bot.py`) drives `Chat`-scoped, per-content-type
`handle()` dispatch for incoming messages. It's missing several valid
`Message` fields that already exist in `TG_Message`:
`"animation"`, `"dice"`, `"video_note"`, `"poll"` (a message can contain a
native poll regardless of whether it was sent via our own `send_poll`).
Add these four.

### 4. Type completions

Replace `= Any` with real `TypedDict`s only for types the above methods
actually send, receive, or return:
`TG_Poll`, `TG_PollAnswer`, `TG_Dice`, `TG_Contact`, `TG_Venue`,
`TG_Location`, `TG_ChatJoinRequest`, `TG_ChatBoostUpdated`,
`TG_ChatBoostRemoved`, `TG_ChatMemberUpdated`, `TG_MessageReactionUpdated`,
`TG_MessageReactionCountUpdated`. Plus one new `TG_XxxOpts`/`TG_XxxOpts_API`
per new method requiring options, following the existing naming and
`total=False` + `Required[...]`/`NotRequired[...]` conventions already in
`types_.py`.

Everything else stays `Any` — no unrelated stub gets filled in.

**Implementation note:** several recently-added methods gained a common
`business_connection_id` optional field across many unrelated endpoints
(already visible in existing types like `TG_SendLocationOpts`,
`TG_SendMediaGroupOpts`, `TG_EditMessageReplyMarkupOpts`). When writing
each new `Opts` type, check the live doc anchor for that method
(`https://core.telegram.org/bots/api#<methodnamelowercased>`) rather than
relying purely on pre-cutoff knowledge — several methods in this list may
have picked up new optional fields since this library's types were last
updated.

### 5. Backward compatibility

`Chat.kick_chat_member` and `Chat.get_chat_members_count` become thin
deprecated aliases that call the new `ban_chat_member`/
`get_chat_member_count` (docstring-flagged `Deprecated: use ... instead`,
no `DeprecationWarning` machinery — consistent with "don't add
infrastructure beyond what's asked"). Those in turn call the current API
method names (`banChatMember`, `getChatMemberCount`) instead of the dead
ones. No existing public signature changes.

### 6. Testing

Each new method gets a `MockBot`-based assertion (correct Telegram method
name + params reach `api_call`), matching the existing style in
`tests/test_chat.py` and `tests/test_api.py`. Each new dispatch branch
gets a case in `tests/test_callbacks.py` style, feeding `_process_update`
a synthetic update and asserting the right decorator fires. The two
backward-compat aliases get a test asserting they call the *new* API
method name, not the old one.

## File impact summary

| File | Change |
|---|---|
| `aiotg/bot.py` | + ~15 `Bot`-level methods, + 9 inbound handler decorators + dispatch branches, `MESSAGE_TYPES` +4 entries |
| `aiotg/chat.py` | + ~35 `Chat`-level methods, 2 existing methods fixed (deprecated aliases added), `forward_message` gains `**options` |
| `aiotg/types_.py` | ~12 `Any` stubs replaced with real `TypedDict`s, ~35 new `Opts`/response `TypedDict`s, existing-but-unused types wired up |
| `tests/test_chat.py`, `tests/test_api.py`, `tests/test_callbacks.py` | new cases per method/dispatch branch |

## Open questions for implementation

- Exact optional-field lists for each new `Opts` TypedDict should be
  verified against the live API reference per method rather than assumed,
  per the `business_connection_id` note above.
- Order of implementation within Phase 1 (e.g. chat administration before
  stickers) is left to the implementation plan — no dependency between
  groups.
