# Telegram Bot API Catch-up (Phase 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the long-missing "core" Telegram Bot API methods (chat administration, forum topics, bot profile/commands, stickers, message-editing/copy/forward completeness) and wire up 9 inbound update types that already exist in `TG_Update` but have no dispatch path, while fixing two existing methods that call renamed/dead API method names.

**Architecture:** Every new method is a thin wrapper following the exact pattern already used throughout `aiotg/chat.py` and `aiotg/bot.py`: build the Telegram API method name, forward required args explicitly, accept `**options: Unpack[TG_XxxOpts]` for optional fields, `return self.bot.api_call(...)` (from `Chat`) or `self.api_call(...)` (from `Bot`). Inbound update handlers reuse the simplest existing dispatch pattern (`bot.default`/`bot.not_handled_update`'s single settable callback), not the regex `_register()` machinery. No new source files; two new test files (`tests/test_bot.py` for new `Bot`-level methods, extending `tests/test_chat.py` for new `Chat`-level methods) since neither has an established home in the current test layout.

**Tech Stack:** Python 3.12+, `TypedDict`-based static typing (no runtime validation), `pytest`, the existing `MockBot` test double (`aiotg/mock.py`).

**Spec:** [docs/superpowers/specs/2026-09-16-bot-api-catchup-design.md](../specs/2026-09-16-bot-api-catchup-design.md)

## Global Constraints

- Every new method mirrors the existing thin-wrapper style — no added validation, no guarding beyond what Telegram's own API enforces (e.g. no `chat.is_group()` pre-checks).
- Deprecated aliases (`kick_chat_member`, `get_chat_members_count`) get a one-line `Deprecated: use X instead.` docstring note only — no `DeprecationWarning`/`warnings.warn` machinery (not in the spec, don't add it).
- Several existing types in `types_.py` (`TG_BanChatMemberOpts`, `TG_UnbanChatMemberOpts`, `TG_RestrictChatMemberOpts`, `TG_PromoteChatMemberOpts`, `TG_SetChatPermissionsOpts`, `TG_CreateChatInviteLinkOpts`, `TG_CreateForumTopicOpts`, `TG_ForwardMessageOpts`) bundle **required** call parameters (`chat_id`, `user_id`, etc.) together with genuinely optional fields inside one `Unpack`-style type. That's inconsistent with every other `Unpack[TG_SendXxxOpts]` in the codebase, where required params are explicit function arguments and only true extras live in the Opts type. None of these 8 types are imported/used anywhere today (verified — safe to reshape). Each task below that touches one of these fixes it to drop the required fields, keeping only the real optional ones.
- Field lists below reflect accurate, high-confidence knowledge of long-stable Bot API methods, but were not re-verified against the live docs method-by-method while writing this plan (the spec already flags this). Before implementing each method, sanity-check its optional-field list against `https://core.telegram.org/bots/api#<methodnamelowercased>` — particularly for a `business_connection_id` field, which many methods have picked up in recent API versions.
- Tasks touch overlapping files (`chat.py`, `bot.py`, `types_.py`) — execute in order, not in parallel; two tasks editing the same file concurrently will conflict.
- Deeply-nested sub-objects that aren't central to a method's main use (`ChatBoostSource`, `ReactionCount`, `BotCommandScope`, `MenuButton`, `InputMedia`) are deliberately typed `dict[str, Any]`/`Any` rather than fully modeled — consistent with existing precedent (`TG_ChatFullInfo.business_intro: Any`, etc.) and flagged inline with a `# ponytail:` comment per Ponytail convention where the simplification is made in a new type.
- Run the targeted test file after every implementation step with `pytest tests/<file>.py -v`; run the full suite (`pytest`) at the end of each task before committing.

---

## Task 1: Fix broken renamed methods (`ban_chat_member`, `get_chat_member_count`)

**Files:**
- Modify: `aiotg/chat.py:131-135` (`get_chat_members_count`), `aiotg/chat.py:433-440` (`kick_chat_member`)
- Modify: `aiotg/types_.py:909-913` (`TG_BanChatMemberOpts`)
- Test: `tests/test_chat.py`

**Interfaces:**
- Consumes: existing `Chat.bot.api_call`, existing `TG_BoolResponse`, `TG_GetChatMemberCountResponse` (already correctly named/shaped in `types_.py:973-975`).
- Produces: `Chat.ban_chat_member(user_id, **options)`, `Chat.get_chat_member_count()` — used by no other task, but this is the canonical name later tasks' docs/tests should reference instead of the deprecated ones.

- [ ] **Step 1: Fix `TG_BanChatMemberOpts`'s shape and write the failing tests**

In `aiotg/types_.py`, replace:
```python
class TG_BanChatMemberOpts(TypedDict, total=False):
    chat_id: Required[str | int]
    user_id: Required[int]
    until_date: int
    revoke_messages: bool
```
with:
```python
class TG_BanChatMemberOpts(TypedDict, total=False):
    until_date: int
    revoke_messages: bool
```

Add to `tests/test_chat.py` (add `from aiotg.mock import MockBot` to its imports):
```python
def test_ban_chat_member_and_deprecated_kick_alias() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.ban_chat_member(7)
    assert bot.calls["banChatMember"]["user_id"] == 7
    assert "kickChatMember" not in bot.calls

    chat.kick_chat_member(8)
    assert bot.calls["banChatMember"]["user_id"] == 8


def test_get_chat_member_count_and_deprecated_alias() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.get_chat_member_count()
    assert "getChatMemberCount" in bot.calls
    assert "getChatMembersCount" not in bot.calls

    chat.get_chat_members_count()
    assert bot.calls["getChatMemberCount"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_chat.py -v -k "ban_chat_member or get_chat_member_count"`
Expected: FAIL — `AttributeError: 'Chat' object has no attribute 'ban_chat_member'`

- [ ] **Step 3: Implement**

In `aiotg/chat.py`, add `TG_BanChatMemberOpts` to the `from .types_ import (...)` block, then replace the `kick_chat_member` method (lines 433-440) with:
```python
    def ban_chat_member(
        self, user_id: int, **options: Unpack[TG_BanChatMemberOpts]
    ) -> Awaitable[TG_BoolResponse]:
        """
        Ban a user from a group, supergroup or channel.
        The bot must be an administrator in the chat for this to work.

        :param int user_id: Unique identifier of the target user
        :param options: Additional banChatMember options (see
            https://core.telegram.org/bots/api#banchatmember)
        """
        return self.bot.api_call(
            "banChatMember", chat_id=self.id, user_id=user_id, **options
        )

    def kick_chat_member(
        self, user_id: int, **options: Unpack[TG_BanChatMemberOpts]
    ) -> Awaitable[TG_BoolResponse]:
        """
        Deprecated: use ban_chat_member instead.
        """
        return self.ban_chat_member(user_id, **options)
```

Replace `get_chat_members_count` (lines 131-135) with:
```python
    def get_chat_member_count(self) -> Awaitable[TG_GetChatMemberCountResponse]:
        """
        Get the number of members in a chat.
        """
        return self.bot.api_call("getChatMemberCount", chat_id=str(self.id))

    def get_chat_members_count(self) -> Awaitable[TG_GetChatMemberCountResponse]:
        """
        Deprecated: use get_chat_member_count instead.
        """
        return self.get_chat_member_count()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_chat.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add aiotg/chat.py aiotg/types_.py tests/test_chat.py
git commit -m "fix: ban_chat_member/get_chat_member_count use current API method names

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 2: Chat membership & permissions

**Files:**
- Modify: `aiotg/chat.py` (insert after the new `ban_chat_member`/`kick_chat_member` pair), `aiotg/types_.py` (`TG_RestrictChatMemberOpts`, `TG_PromoteChatMemberOpts`, `TG_SetChatPermissionsOpts` — locate by name; Task 1's edit already shifted these from their original line numbers)
- Test: `tests/test_chat.py`

**Interfaces:**
- Consumes: existing `TG_ChatPermissions` (`types_.py:147-161`), `TG_AdminPermissions` (`types_.py:164-179`) — both already correctly shaped, reused as-is.
- Produces: `Chat.restrict_chat_member`, `Chat.promote_chat_member`, `Chat.set_chat_administrator_custom_title`, `Chat.ban_chat_sender_chat`, `Chat.unban_chat_sender_chat`, `Chat.set_chat_permissions`.

- [ ] **Step 1: Fix the three Opts types and write the failing tests**

In `aiotg/types_.py`, replace:
```python
class TG_RestrictChatMemberOpts(TypedDict, total=True):
    chat_id: str | int
    user_id: int
    permissions: TG_ChatPermissions
    use_independent_chat_permissions: NotRequired[bool]
    until_date: NotRequired[int]
```
with:
```python
class TG_RestrictChatMemberOpts(TypedDict, total=False):
    use_independent_chat_permissions: bool
    until_date: int
```

Replace:
```python
class TG_PromoteChatMemberOpts(TG_AdminPermissions, total=False):
    chat_id: Required[str | int]
    user_id: Required[int]
    is_anonymous: bool
```
with:
```python
class TG_PromoteChatMemberOpts(TG_AdminPermissions, total=False):
    is_anonymous: bool
```

Replace:
```python
class TG_SetChatPermissionsOpts(TypedDict, total=True):
    chat_id: str | int
    permissions: TG_ChatPermissions
    use_independent_chat_permissions: NotRequired[bool]
```
with:
```python
class TG_SetChatPermissionsOpts(TypedDict, total=False):
    use_independent_chat_permissions: bool
```

Add to `tests/test_chat.py`:
```python
def test_restrict_and_promote_chat_member() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.restrict_chat_member(7, {"can_send_messages": False})
    assert bot.calls["restrictChatMember"]["permissions"] == {
        "can_send_messages": False
    }

    chat.promote_chat_member(7, can_delete_messages=True)
    assert bot.calls["promoteChatMember"]["can_delete_messages"] is True


def test_chat_administrator_custom_title_and_sender_chat_bans() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.set_chat_administrator_custom_title(7, "Mod")
    assert bot.calls["setChatAdministratorCustomTitle"]["custom_title"] == "Mod"

    chat.ban_chat_sender_chat(99)
    assert bot.calls["banChatSenderChat"]["sender_chat_id"] == 99

    chat.unban_chat_sender_chat(99)
    assert bot.calls["unbanChatSenderChat"]["sender_chat_id"] == 99


def test_set_chat_permissions() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.set_chat_permissions({"can_send_messages": True})
    assert bot.calls["setChatPermissions"]["permissions"] == {
        "can_send_messages": True
    }
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_chat.py -v -k "restrict_and_promote or custom_title or set_chat_permissions"`
Expected: FAIL — `AttributeError`

- [ ] **Step 3: Implement**

Add `TG_RestrictChatMemberOpts`, `TG_PromoteChatMemberOpts`, `TG_SetChatPermissionsOpts`, `TG_ChatPermissions` to `chat.py`'s `from .types_ import (...)` block, then add to `Chat`:
```python
    def restrict_chat_member(
        self,
        user_id: int,
        permissions: TG_ChatPermissions,
        **options: Unpack[TG_RestrictChatMemberOpts],
    ) -> Awaitable[TG_BoolResponse]:
        """
        Restrict a user in a supergroup.
        The bot must be an administrator in the supergroup for this to work.

        :param int user_id: Unique identifier of the target user
        :param dict permissions: New user permissions
        :param options: Additional restrictChatMember options (see
            https://core.telegram.org/bots/api#restrictchatmember)
        """
        return self.bot.api_call(
            "restrictChatMember",
            chat_id=self.id,
            user_id=user_id,
            permissions=permissions,
            **options,
        )

    def promote_chat_member(
        self, user_id: int, **options: Unpack[TG_PromoteChatMemberOpts]
    ) -> Awaitable[TG_BoolResponse]:
        """
        Promote or demote a user in a supergroup or channel.
        The bot must be an administrator in the chat for this to work.

        :param int user_id: Unique identifier of the target user
        :param options: Which admin rights to grant (see
            https://core.telegram.org/bots/api#promotechatmember)
        """
        return self.bot.api_call(
            "promoteChatMember", chat_id=self.id, user_id=user_id, **options
        )

    def set_chat_administrator_custom_title(
        self, user_id: int, custom_title: str
    ) -> Awaitable[TG_BoolResponse]:
        """
        Set a custom title for an administrator in a supergroup.

        :param int user_id: Unique identifier of the target user
        :param str custom_title: New custom title for the administrator
        """
        return self.bot.api_call(
            "setChatAdministratorCustomTitle",
            chat_id=self.id,
            user_id=user_id,
            custom_title=custom_title,
        )

    def ban_chat_sender_chat(self, sender_chat_id: int) -> Awaitable[TG_BoolResponse]:
        """
        Ban a channel chat in a supergroup or channel.

        :param int sender_chat_id: Unique identifier of the target sender chat
        """
        return self.bot.api_call(
            "banChatSenderChat", chat_id=self.id, sender_chat_id=sender_chat_id
        )

    def unban_chat_sender_chat(
        self, sender_chat_id: int
    ) -> Awaitable[TG_BoolResponse]:
        """
        Unban a previously banned channel chat in a supergroup or channel.

        :param int sender_chat_id: Unique identifier of the target sender chat
        """
        return self.bot.api_call(
            "unbanChatSenderChat", chat_id=self.id, sender_chat_id=sender_chat_id
        )

    def set_chat_permissions(
        self,
        permissions: TG_ChatPermissions,
        **options: Unpack[TG_SetChatPermissionsOpts],
    ) -> Awaitable[TG_BoolResponse]:
        """
        Set default chat permissions for all members.
        The bot must be an administrator and have can_restrict_members rights.

        :param dict permissions: New default chat permissions
        :param options: Additional setChatPermissions options (see
            https://core.telegram.org/bots/api#setchatpermissions)
        """
        return self.bot.api_call(
            "setChatPermissions", chat_id=self.id, permissions=permissions, **options
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_chat.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add aiotg/chat.py aiotg/types_.py tests/test_chat.py
git commit -m "feat: add chat membership and permission management methods

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 3: Chat invite links & join requests

**Files:**
- Modify: `aiotg/chat.py` (insert after Task 2's methods), `aiotg/types_.py` (`TG_CreateChatInviteLinkOpts` — locate by name, lines have shifted)
- Test: `tests/test_chat.py`

**Interfaces:**
- Consumes: existing `TG_CreateChatInviteLinkResponse` (`types_.py:1008-1010`), existing `TG_StringResponse` (`types_.py:998-1000`).
- Produces: `Chat.export_chat_invite_link`, `Chat.create_chat_invite_link`, `Chat.edit_chat_invite_link`, `Chat.revoke_chat_invite_link`, `Chat.approve_chat_join_request`, `Chat.decline_chat_join_request`.

- [ ] **Step 1: Fix `TG_CreateChatInviteLinkOpts` and write the failing tests**

In `aiotg/types_.py`, replace:
```python
class TG_CreateChatInviteLinkOpts(TypedDict, total=False):
    chat_id: str | int
    name: NotRequired[str]
    expire_date: NotRequired[int]
    member_limit: NotRequired[int]
    creates_join_request: NotRequired[bool]
```
with:
```python
class TG_CreateChatInviteLinkOpts(TypedDict, total=False):
    name: str
    expire_date: int
    member_limit: int
    creates_join_request: bool
```
(dropping `chat_id`, which doesn't belong in the options type — every other `Unpack[TG_SendXxxOpts]` in the codebase excludes it too. The fields left are also exactly what `editChatInviteLink` accepts, so this one type is reused for both create and edit.)

Add to `tests/test_chat.py`:
```python
def test_chat_invite_links() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.export_chat_invite_link()
    assert "exportChatInviteLink" in bot.calls

    chat.create_chat_invite_link(name="Marketing")
    assert bot.calls["createChatInviteLink"]["name"] == "Marketing"

    chat.edit_chat_invite_link("https://t.me/joinchat/abc", member_limit=10)
    assert bot.calls["editChatInviteLink"]["invite_link"] == "https://t.me/joinchat/abc"
    assert bot.calls["editChatInviteLink"]["member_limit"] == 10

    chat.revoke_chat_invite_link("https://t.me/joinchat/abc")
    assert bot.calls["revokeChatInviteLink"]["invite_link"] == "https://t.me/joinchat/abc"


def test_chat_join_requests() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.approve_chat_join_request(7)
    assert bot.calls["approveChatJoinRequest"]["user_id"] == 7

    chat.decline_chat_join_request(7)
    assert bot.calls["declineChatJoinRequest"]["user_id"] == 7
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_chat.py -v -k "invite_links or join_requests"`
Expected: FAIL — `AttributeError`

- [ ] **Step 3: Implement**

Add `TG_CreateChatInviteLinkOpts`, `TG_CreateChatInviteLinkResponse`, `TG_StringResponse` to `chat.py`'s type imports, then add to `Chat`:
```python
    def export_chat_invite_link(self) -> Awaitable[TG_StringResponse]:
        """
        Generate a new primary invite link for the chat, revoking any previous one.
        The bot must be an administrator with can_invite_users rights.
        """
        return self.bot.api_call("exportChatInviteLink", chat_id=self.id)

    def create_chat_invite_link(
        self, **options: Unpack[TG_CreateChatInviteLinkOpts]
    ) -> Awaitable[TG_CreateChatInviteLinkResponse]:
        """
        Create an additional invite link for the chat.
        The bot must be an administrator with can_invite_users rights.

        :param options: Additional createChatInviteLink options (see
            https://core.telegram.org/bots/api#createchatinvitelink)
        """
        return self.bot.api_call("createChatInviteLink", chat_id=self.id, **options)

    def edit_chat_invite_link(
        self, invite_link: str, **options: Unpack[TG_CreateChatInviteLinkOpts]
    ) -> Awaitable[TG_CreateChatInviteLinkResponse]:
        """
        Edit a non-primary invite link created by the bot.

        :param str invite_link: The invite link to edit
        :param options: Additional editChatInviteLink options (see
            https://core.telegram.org/bots/api#editchatinvitelink)
        """
        return self.bot.api_call(
            "editChatInviteLink", chat_id=self.id, invite_link=invite_link, **options
        )

    def revoke_chat_invite_link(
        self, invite_link: str
    ) -> Awaitable[TG_CreateChatInviteLinkResponse]:
        """
        Revoke an invite link created by the bot.

        :param str invite_link: The invite link to revoke
        """
        return self.bot.api_call(
            "revokeChatInviteLink", chat_id=self.id, invite_link=invite_link
        )

    def approve_chat_join_request(self, user_id: int) -> Awaitable[TG_BoolResponse]:
        """
        Approve a chat join request.
        The bot must have can_invite_users rights.

        :param int user_id: Unique identifier of the target user
        """
        return self.bot.api_call(
            "approveChatJoinRequest", chat_id=self.id, user_id=user_id
        )

    def decline_chat_join_request(self, user_id: int) -> Awaitable[TG_BoolResponse]:
        """
        Decline a chat join request.
        The bot must have can_invite_users rights.

        :param int user_id: Unique identifier of the target user
        """
        return self.bot.api_call(
            "declineChatJoinRequest", chat_id=self.id, user_id=user_id
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_chat.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add aiotg/chat.py aiotg/types_.py tests/test_chat.py
git commit -m "feat: add chat invite link and join request methods

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 4: Chat metadata & pinning

**Files:**
- Modify: `aiotg/chat.py` (insert after Task 3's methods), `aiotg/types_.py` (add two new Opts types near `TG_CreateChatInviteLinkOpts`)
- Test: `tests/test_chat.py`

**Interfaces:**
- Consumes: existing `TG_SendFileInput` (`types_.py:778`), `TG_BoolResponse`.
- Produces: `Chat.set_chat_photo`, `Chat.delete_chat_photo`, `Chat.set_chat_title`, `Chat.set_chat_description`, `Chat.pin_chat_message`, `Chat.unpin_chat_message`, `Chat.unpin_all_chat_messages`.

- [ ] **Step 1: Add two new Opts types and write the failing tests**

Add to `aiotg/types_.py` (near the other chat-admin Opts types):
```python
class TG_PinChatMessageOpts(TypedDict, total=False):
    business_connection_id: str
    disable_notification: bool


class TG_UnpinChatMessageOpts(TypedDict, total=False):
    business_connection_id: str
    message_id: int
```

Add to `tests/test_chat.py`:
```python
def test_chat_photo_and_metadata() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.set_chat_photo(b"foo")
    assert "setChatPhoto" in bot.calls

    chat.delete_chat_photo()
    assert "deleteChatPhoto" in bot.calls

    chat.set_chat_title("New Title")
    assert bot.calls["setChatTitle"]["title"] == "New Title"

    chat.set_chat_description("New description")
    assert bot.calls["setChatDescription"]["description"] == "New description"


def test_pin_and_unpin_chat_message() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.pin_chat_message(1337)
    assert bot.calls["pinChatMessage"]["message_id"] == 1337

    chat.unpin_chat_message(message_id=1337)
    assert bot.calls["unpinChatMessage"]["message_id"] == 1337

    chat.unpin_all_chat_messages()
    assert "unpinAllChatMessages" in bot.calls
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_chat.py -v -k "chat_photo or pin_and_unpin"`
Expected: FAIL — `AttributeError`

- [ ] **Step 3: Implement**

Add `TG_PinChatMessageOpts`, `TG_UnpinChatMessageOpts` to `chat.py`'s type imports, then add to `Chat`:
```python
    def set_chat_photo(self, photo: TG_SendFileInput) -> Awaitable[TG_BoolResponse]:
        """
        Set a new profile photo for the chat.
        The bot must be an administrator with can_change_info rights.

        :param photo: New chat photo (file, not a file_id or URL)
        """
        return self.bot.api_call("setChatPhoto", chat_id=self.id, photo=photo)

    def delete_chat_photo(self) -> Awaitable[TG_BoolResponse]:
        """
        Delete the chat's profile photo.
        The bot must be an administrator with can_change_info rights.
        """
        return self.bot.api_call("deleteChatPhoto", chat_id=self.id)

    def set_chat_title(self, title: str) -> Awaitable[TG_BoolResponse]:
        """
        Change the title of the chat.
        The bot must be an administrator with can_change_info rights.

        :param str title: New chat title, 1-128 characters
        """
        return self.bot.api_call("setChatTitle", chat_id=self.id, title=title)

    def set_chat_description(self, description: str = "") -> Awaitable[TG_BoolResponse]:
        """
        Change the description of the chat.
        The bot must be an administrator with can_change_info rights.

        :param str description: New chat description, 0-255 characters
        """
        return self.bot.api_call(
            "setChatDescription", chat_id=self.id, description=description
        )

    def pin_chat_message(
        self, message_id: int, **options: Unpack[TG_PinChatMessageOpts]
    ) -> Awaitable[TG_BoolResponse]:
        """
        Pin a message in the chat.
        The bot must be an administrator with can_pin_messages rights.

        :param int message_id: Identifier of the message to pin
        :param options: Additional pinChatMessage options (see
            https://core.telegram.org/bots/api#pinchatmessage)
        """
        return self.bot.api_call(
            "pinChatMessage", chat_id=self.id, message_id=message_id, **options
        )

    def unpin_chat_message(
        self, **options: Unpack[TG_UnpinChatMessageOpts]
    ) -> Awaitable[TG_BoolResponse]:
        """
        Unpin a message in the chat. Unpins the most recent pinned message if
        message_id isn't specified.

        :param options: Additional unpinChatMessage options, including
            message_id (see https://core.telegram.org/bots/api#unpinchatmessage)
        """
        return self.bot.api_call("unpinChatMessage", chat_id=self.id, **options)

    def unpin_all_chat_messages(self) -> Awaitable[TG_BoolResponse]:
        """
        Unpin all pinned messages in the chat.
        The bot must be an administrator with can_pin_messages rights.
        """
        return self.bot.api_call("unpinAllChatMessages", chat_id=self.id)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_chat.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add aiotg/chat.py aiotg/types_.py tests/test_chat.py
git commit -m "feat: add chat photo, title, description and pin management methods

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 5: Forum topics

**Files:**
- Modify: `aiotg/chat.py` (insert after Task 4's methods), `aiotg/bot.py` (insert `get_forum_topic_icon_stickers` near `get_user_profile_photos`, `aiotg/bot.py:669-679` — still accurate, no prior task has touched `bot.py`), `aiotg/types_.py` (`TG_CreateForumTopicOpts` — locate by name, lines have shifted)
- Test: `tests/test_chat.py`, `tests/test_bot.py` (new file)

**Interfaces:**
- Consumes: existing `TG_CreateForumTopicResponse` (`types_.py:988-990`), `TG_BoolResponse`.
- Produces: `Chat.create_forum_topic`, `.edit_forum_topic`, `.close_forum_topic`, `.reopen_forum_topic`, `.delete_forum_topic`, `.unpin_all_forum_topic_messages`, `.edit_general_forum_topic`, `.close_general_forum_topic`, `.reopen_general_forum_topic`, `.hide_general_forum_topic`, `.unhide_general_forum_topic`, `.unpin_all_general_forum_topic_messages`; `Bot.get_forum_topic_icon_stickers`.

- [ ] **Step 1: Fix `TG_CreateForumTopicOpts`, add `TG_EditForumTopicOpts`, and write the failing tests**

In `aiotg/types_.py`, replace:
```python
class TG_CreateForumTopicOpts(TypedDict, total=False):
    chat_id: Required[str | int]
    name: Required[str]
    icon_color: int
    icon_custom_emoji_id: str
```
with:
```python
class TG_CreateForumTopicOpts(TypedDict, total=False):
    icon_color: int
    icon_custom_emoji_id: str


class TG_EditForumTopicOpts(TypedDict, total=False):
    name: str
    icon_custom_emoji_id: str
```
(`name` moves to an explicit required positional argument on `create_forum_topic`, matching every other required-field method in the codebase.)

Add to `tests/test_chat.py`:
```python
def test_forum_topic_management() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.create_forum_topic("General", icon_color=0x6FB9F0)
    assert bot.calls["createForumTopic"]["name"] == "General"

    chat.edit_forum_topic(5, name="Renamed")
    assert bot.calls["editForumTopic"]["message_thread_id"] == 5

    chat.close_forum_topic(5)
    assert bot.calls["closeForumTopic"]["message_thread_id"] == 5

    chat.reopen_forum_topic(5)
    assert bot.calls["reopenForumTopic"]["message_thread_id"] == 5

    chat.delete_forum_topic(5)
    assert bot.calls["deleteForumTopic"]["message_thread_id"] == 5

    chat.unpin_all_forum_topic_messages(5)
    assert bot.calls["unpinAllForumTopicMessages"]["message_thread_id"] == 5


def test_general_forum_topic_management() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.edit_general_forum_topic("Renamed General")
    assert bot.calls["editGeneralForumTopic"]["name"] == "Renamed General"

    chat.close_general_forum_topic()
    assert "closeGeneralForumTopic" in bot.calls

    chat.reopen_general_forum_topic()
    assert "reopenGeneralForumTopic" in bot.calls

    chat.hide_general_forum_topic()
    assert "hideGeneralForumTopic" in bot.calls

    chat.unhide_general_forum_topic()
    assert "unhideGeneralForumTopic" in bot.calls

    chat.unpin_all_general_forum_topic_messages()
    assert "unpinAllGeneralForumTopicMessages" in bot.calls
```

Create `tests/test_bot.py`:
```python
from aiotg.mock import MockBot


def test_get_forum_topic_icon_stickers() -> None:
    bot = MockBot()

    bot.get_forum_topic_icon_stickers()
    assert "getForumTopicIconStickers" in bot.calls
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_chat.py tests/test_bot.py -v -k "forum_topic"`
Expected: FAIL — `AttributeError`

- [ ] **Step 3: Implement**

Add `TG_CreateForumTopicOpts`, `TG_EditForumTopicOpts`, `TG_CreateForumTopicResponse` to `chat.py`'s type imports, then add to `Chat`:
```python
    def create_forum_topic(
        self, name: str, **options: Unpack[TG_CreateForumTopicOpts]
    ) -> Awaitable[TG_CreateForumTopicResponse]:
        """
        Create a topic in a forum supergroup.
        The bot must be an administrator with can_manage_topics rights.

        :param str name: Topic name, 1-128 characters
        :param options: Additional createForumTopic options (see
            https://core.telegram.org/bots/api#createforumtopic)
        """
        return self.bot.api_call(
            "createForumTopic", chat_id=self.id, name=name, **options
        )

    def edit_forum_topic(
        self, message_thread_id: int, **options: Unpack[TG_EditForumTopicOpts]
    ) -> Awaitable[TG_BoolResponse]:
        """
        Edit the name and icon of a topic in a forum supergroup.

        :param int message_thread_id: Unique identifier of the target topic
        :param options: Additional editForumTopic options (see
            https://core.telegram.org/bots/api#editforumtopic)
        """
        return self.bot.api_call(
            "editForumTopic",
            chat_id=self.id,
            message_thread_id=message_thread_id,
            **options,
        )

    def close_forum_topic(self, message_thread_id: int) -> Awaitable[TG_BoolResponse]:
        """
        Close an open topic in a forum supergroup.

        :param int message_thread_id: Unique identifier of the target topic
        """
        return self.bot.api_call(
            "closeForumTopic", chat_id=self.id, message_thread_id=message_thread_id
        )

    def reopen_forum_topic(
        self, message_thread_id: int
    ) -> Awaitable[TG_BoolResponse]:
        """
        Reopen a closed topic in a forum supergroup.

        :param int message_thread_id: Unique identifier of the target topic
        """
        return self.bot.api_call(
            "reopenForumTopic", chat_id=self.id, message_thread_id=message_thread_id
        )

    def delete_forum_topic(
        self, message_thread_id: int
    ) -> Awaitable[TG_BoolResponse]:
        """
        Delete a forum topic along with all its messages.
        The bot must have can_delete_messages rights.

        :param int message_thread_id: Unique identifier of the target topic
        """
        return self.bot.api_call(
            "deleteForumTopic", chat_id=self.id, message_thread_id=message_thread_id
        )

    def unpin_all_forum_topic_messages(
        self, message_thread_id: int
    ) -> Awaitable[TG_BoolResponse]:
        """
        Unpin all pinned messages in a forum topic.

        :param int message_thread_id: Unique identifier of the target topic
        """
        return self.bot.api_call(
            "unpinAllForumTopicMessages",
            chat_id=self.id,
            message_thread_id=message_thread_id,
        )

    def edit_general_forum_topic(self, name: str) -> Awaitable[TG_BoolResponse]:
        """
        Edit the name of the 'General' topic in a forum supergroup.

        :param str name: New topic name, 1-128 characters
        """
        return self.bot.api_call(
            "editGeneralForumTopic", chat_id=self.id, name=name
        )

    def close_general_forum_topic(self) -> Awaitable[TG_BoolResponse]:
        """Close the 'General' topic in a forum supergroup."""
        return self.bot.api_call("closeGeneralForumTopic", chat_id=self.id)

    def reopen_general_forum_topic(self) -> Awaitable[TG_BoolResponse]:
        """Reopen the 'General' topic in a forum supergroup (also unhides it)."""
        return self.bot.api_call("reopenGeneralForumTopic", chat_id=self.id)

    def hide_general_forum_topic(self) -> Awaitable[TG_BoolResponse]:
        """Hide the 'General' topic in a forum supergroup (also closes it)."""
        return self.bot.api_call("hideGeneralForumTopic", chat_id=self.id)

    def unhide_general_forum_topic(self) -> Awaitable[TG_BoolResponse]:
        """Unhide the 'General' topic in a forum supergroup."""
        return self.bot.api_call("unhideGeneralForumTopic", chat_id=self.id)

    def unpin_all_general_forum_topic_messages(self) -> Awaitable[TG_BoolResponse]:
        """Unpin all pinned messages in the 'General' topic."""
        return self.bot.api_call(
            "unpinAllGeneralForumTopicMessages", chat_id=self.id
        )
```

In `aiotg/bot.py`, add after `get_user_profile_photos` (line 679):
```python
    def get_forum_topic_icon_stickers(self) -> Awaitable[Any]:
        """
        Get custom emoji stickers that can be used as forum topic icons.
        """
        return self.api_call("getForumTopicIconStickers")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_chat.py tests/test_bot.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add aiotg/chat.py aiotg/bot.py aiotg/types_.py tests/test_chat.py tests/test_bot.py
git commit -m "feat: add forum topic management methods

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 6: Bot profile & commands

**Files:**
- Modify: `aiotg/bot.py` (insert after Task 5's `get_forum_topic_icon_stickers`), `aiotg/types_.py` (new types, add near `TG_AdminPermissions`)
- Test: `tests/test_bot.py`

**Interfaces:**
- Consumes: existing `TG_AdminPermissions` (`types_.py:164-179`, reused for `set_my_default_administrator_rights`'s `rights` param).
- Produces: `Bot.set_my_commands`, `.get_my_commands`, `.delete_my_commands`, `.set_my_name`, `.get_my_name`, `.set_my_description`, `.get_my_description`, `.set_my_short_description`, `.get_my_short_description`, `.set_chat_menu_button`, `.get_chat_menu_button`, `.set_my_default_administrator_rights`, `.get_my_default_administrator_rights`.

- [ ] **Step 1: Add new types and write the failing tests**

Add to `aiotg/types_.py`:
```python
class TG_BotCommand(TypedDict, total=True):
    command: str
    description: str


# ponytail: scope/menu_button typed loosely rather than modeling the full
# BotCommandScope (7 variants) / MenuButton (3 variants) unions — expand to
# real TypedDict unions if a caller needs static checking of scope/button kind
class TG_BotCommandScopeOpts(TypedDict, total=False):
    scope: dict[str, Any]
    language_code: str


class TG_LanguageCodeOpts(TypedDict, total=False):
    language_code: str


class TG_ChatMenuButtonOpts(TypedDict, total=False):
    chat_id: int | str
    menu_button: dict[str, Any]


class TG_DefaultAdministratorRightsOpts(TypedDict, total=False):
    rights: TG_AdminPermissions
    for_channels: bool
```

Add to `tests/test_bot.py` (no new imports needed — `MockBot` is already imported from Task 5):
```python
def test_bot_commands() -> None:
    bot = MockBot()

    bot.set_my_commands([{"command": "start", "description": "Start the bot"}])
    assert bot.calls["setMyCommands"]["commands"] == [
        {"command": "start", "description": "Start the bot"}
    ]

    bot.get_my_commands()
    assert "getMyCommands" in bot.calls

    bot.delete_my_commands()
    assert "deleteMyCommands" in bot.calls


def test_bot_profile_text() -> None:
    bot = MockBot()

    bot.set_my_name(name="Foo Bot")
    assert bot.calls["setMyName"]["name"] == "Foo Bot"
    bot.get_my_name()
    assert "getMyName" in bot.calls

    bot.set_my_description(description="Does foo.")
    assert bot.calls["setMyDescription"]["description"] == "Does foo."
    bot.get_my_description()
    assert "getMyDescription" in bot.calls

    bot.set_my_short_description(short_description="Foo.")
    assert bot.calls["setMyShortDescription"]["short_description"] == "Foo."
    bot.get_my_short_description()
    assert "getMyShortDescription" in bot.calls


def test_chat_menu_button_and_default_admin_rights() -> None:
    bot = MockBot()

    bot.set_chat_menu_button(chat_id=42, menu_button={"type": "commands"})
    assert bot.calls["setChatMenuButton"]["chat_id"] == 42

    bot.get_chat_menu_button()
    assert "getChatMenuButton" in bot.calls

    bot.set_my_default_administrator_rights(rights={"can_change_info": True})
    assert bot.calls["setMyDefaultAdministratorRights"]["rights"] == {
        "can_change_info": True
    }

    bot.get_my_default_administrator_rights()
    assert "getMyDefaultAdministratorRights" in bot.calls
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_bot.py -v`
Expected: FAIL — `AttributeError`

- [ ] **Step 3: Implement**

Add `TG_BotCommand`, `TG_BotCommandScopeOpts`, `TG_LanguageCodeOpts`, `TG_ChatMenuButtonOpts`, `TG_DefaultAdministratorRightsOpts` to `bot.py`'s type imports, then add to `Bot` (after `get_forum_topic_icon_stickers`):
```python
    def set_my_commands(
        self,
        commands: list[TG_BotCommand],
        **options: Unpack[TG_BotCommandScopeOpts],
    ) -> Awaitable[Any]:
        """
        Change the list of the bot's commands.

        :param commands: List of bot commands to set
        :param options: Additional setMyCommands options (see
            https://core.telegram.org/bots/api#setmycommands)
        """
        return self.api_call("setMyCommands", commands=commands, **options)

    def get_my_commands(
        self, **options: Unpack[TG_BotCommandScopeOpts]
    ) -> Awaitable[Any]:
        """
        Get the current list of the bot's commands for the given scope/language.
        """
        return self.api_call("getMyCommands", **options)

    def delete_my_commands(
        self, **options: Unpack[TG_BotCommandScopeOpts]
    ) -> Awaitable[Any]:
        """
        Delete the list of the bot's commands for the given scope/language.
        """
        return self.api_call("deleteMyCommands", **options)

    def set_my_name(
        self, name: str = "", **options: Unpack[TG_LanguageCodeOpts]
    ) -> Awaitable[Any]:
        """
        Change the bot's name.

        :param str name: New bot name, 0-64 characters (empty to remove)
        """
        return self.api_call("setMyName", name=name, **options)

    def get_my_name(self, **options: Unpack[TG_LanguageCodeOpts]) -> Awaitable[Any]:
        """Get the current bot name for the given language."""
        return self.api_call("getMyName", **options)

    def set_my_description(
        self, description: str = "", **options: Unpack[TG_LanguageCodeOpts]
    ) -> Awaitable[Any]:
        """
        Change the bot's description (shown on the empty chat screen).

        :param str description: New description, 0-512 characters
        """
        return self.api_call("setMyDescription", description=description, **options)

    def get_my_description(
        self, **options: Unpack[TG_LanguageCodeOpts]
    ) -> Awaitable[Any]:
        """Get the current bot description for the given language."""
        return self.api_call("getMyDescription", **options)

    def set_my_short_description(
        self, short_description: str = "", **options: Unpack[TG_LanguageCodeOpts]
    ) -> Awaitable[Any]:
        """
        Change the bot's short description (shown on the bot's profile page).

        :param str short_description: New short description, 0-120 characters
        """
        return self.api_call(
            "setMyShortDescription", short_description=short_description, **options
        )

    def get_my_short_description(
        self, **options: Unpack[TG_LanguageCodeOpts]
    ) -> Awaitable[Any]:
        """Get the current bot short description for the given language."""
        return self.api_call("getMyShortDescription", **options)

    def set_chat_menu_button(
        self, **options: Unpack[TG_ChatMenuButtonOpts]
    ) -> Awaitable[Any]:
        """
        Change the bot's menu button in a private chat, or the default menu
        button.

        :param options: Additional setChatMenuButton options (see
            https://core.telegram.org/bots/api#setchatmenubutton)
        """
        return self.api_call("setChatMenuButton", **options)

    def get_chat_menu_button(
        self, chat_id: int | str | None = None
    ) -> Awaitable[Any]:
        """
        Get the current menu button for a private chat, or the default one.

        :param chat_id: Target private chat, or None for the default button
        """
        options: dict[str, Any] = {"chat_id": chat_id} if chat_id is not None else {}
        return self.api_call("getChatMenuButton", **options)

    def set_my_default_administrator_rights(
        self, **options: Unpack[TG_DefaultAdministratorRightsOpts]
    ) -> Awaitable[Any]:
        """
        Change the default administrator rights requested by the bot when
        it's added as an administrator to groups or channels.

        :param options: Additional setMyDefaultAdministratorRights options (see
            https://core.telegram.org/bots/api#setmydefaultadministratorrights)
        """
        return self.api_call("setMyDefaultAdministratorRights", **options)

    def get_my_default_administrator_rights(
        self, for_channels: bool = False
    ) -> Awaitable[Any]:
        """
        Get the current default administrator rights requested by the bot.

        :param bool for_channels: Get rights for channels instead of groups
        """
        return self.api_call(
            "getMyDefaultAdministratorRights", for_channels=for_channels
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_bot.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add aiotg/bot.py aiotg/types_.py tests/test_bot.py
git commit -m "feat: add bot profile and command management methods

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 7: Stickers

**Files:**
- Modify: `aiotg/bot.py` (insert after Task 6's methods; also add `Literal` to the `from typing import (...)` line, which currently doesn't import it), `aiotg/types_.py` (new types, placed directly above `TG_SendMediaGroupOpts` — see Step 1 for why)
- Test: `tests/test_bot.py`

**Interfaces:**
- Consumes: existing `TG_MaskPosition` (`types_.py:6-10`), `TG_SendFileInput` (`types_.py:778`).
- Produces: `Bot.get_sticker_set`, `.get_custom_emoji_stickers`, `.upload_sticker_file`, `.create_new_sticker_set`, `.add_sticker_to_set`, `.set_sticker_position_in_set`, `.delete_sticker_from_set`, `.replace_sticker_in_set`, `.set_sticker_emoji_list`, `.set_sticker_keywords`, `.set_sticker_mask_position`, `.set_sticker_set_title`, `.set_sticker_set_thumbnail`, `.set_custom_emoji_sticker_set_thumbnail`, `.delete_sticker_set`.

- [ ] **Step 1: Add `TG_InputSticker` / `TG_CreateNewStickerSetOpts` and write the failing test**

Add to `aiotg/types_.py` (near `TG_MaskPosition`):
```python
class TG_InputSticker(TypedDict, total=False):
    sticker: Required[TG_SendFileInput]
    format: Required[Literal["static", "animated", "video"]]
    emoji_list: Required[list[str]]
    mask_position: TG_MaskPosition
    keywords: list[str]


class TG_CreateNewStickerSetOpts(TypedDict, total=False):
    sticker_type: Literal["regular", "mask", "custom_emoji"]
    needs_repainting: bool
```
(`TG_SendFileInput` is defined further down the file, at line 778 — move this new block below that definition, or forward-reference it as `"TG_SendFileInput"` if placed above. Simplest: add both new types directly above `TG_SendMediaGroupOpts`, right after the `TG_SendFileInput = TG_InputFile | str` line.)

Add to `tests/test_bot.py`:
```python
from aiotg.types_ import TG_InputSticker


def test_sticker_set_management() -> None:
    bot = MockBot()
    sticker: TG_InputSticker = {
        "sticker": b"foo",
        "format": "static",
        "emoji_list": ["\U0001F600"],
    }

    bot.get_sticker_set("cats")
    assert bot.calls["getStickerSet"]["name"] == "cats"

    bot.get_custom_emoji_stickers(["1", "2"])
    assert bot.calls["getCustomEmojiStickers"]["custom_emoji_ids"] == ["1", "2"]

    bot.upload_sticker_file(7, b"foo", "static")
    assert bot.calls["uploadStickerFile"]["user_id"] == 7

    bot.create_new_sticker_set(7, "cats_by_bot", "Cats", [sticker])
    assert bot.calls["createNewStickerSet"]["name"] == "cats_by_bot"

    bot.add_sticker_to_set(7, "cats_by_bot", sticker)
    assert bot.calls["addStickerToSet"]["name"] == "cats_by_bot"

    bot.set_sticker_position_in_set("CAAA", 2)
    assert bot.calls["setStickerPositionInSet"]["position"] == 2

    bot.delete_sticker_from_set("CAAA")
    assert bot.calls["deleteStickerFromSet"]["sticker"] == "CAAA"

    bot.replace_sticker_in_set(7, "cats_by_bot", "CAAA", sticker)
    assert bot.calls["replaceStickerInSet"]["old_sticker"] == "CAAA"

    bot.set_sticker_emoji_list("CAAA", ["\U0001F600"])
    assert bot.calls["setStickerEmojiList"]["emoji_list"] == ["\U0001F600"]

    bot.set_sticker_keywords("CAAA", ["cat", "meow"])
    assert bot.calls["setStickerKeywords"]["keywords"] == ["cat", "meow"]

    bot.set_sticker_mask_position(
        "CAAA", {"point": "forehead", "x_shift": 0.0, "y_shift": 0.0, "scale": 1.0}
    )
    assert bot.calls["setStickerMaskPosition"]["sticker"] == "CAAA"

    bot.set_sticker_set_title("cats_by_bot", "Cats!")
    assert bot.calls["setStickerSetTitle"]["title"] == "Cats!"

    bot.set_sticker_set_thumbnail("cats_by_bot", 7, "static")
    assert bot.calls["setStickerSetThumbnail"]["format"] == "static"

    bot.set_custom_emoji_sticker_set_thumbnail("cats_by_bot", "1")
    assert bot.calls["setCustomEmojiStickerSetThumbnail"]["custom_emoji_id"] == "1"

    bot.delete_sticker_set("cats_by_bot")
    assert bot.calls["deleteStickerSet"]["name"] == "cats_by_bot"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_bot.py -v -k sticker_set_management`
Expected: FAIL — `AttributeError`

- [ ] **Step 3: Implement**

In `aiotg/bot.py`, change `from typing import Any, Callable, Unpack, overload` to
`from typing import Any, Callable, Literal, Unpack, overload`. Add `TG_InputSticker`, `TG_CreateNewStickerSetOpts`, `TG_MaskPosition` to the `from .types_ import (...)` block, then add to `Bot` (after Task 6's methods):
```python
    def get_sticker_set(self, name: str) -> Awaitable[Any]:
        """Get a sticker set by name."""
        return self.api_call("getStickerSet", name=name)

    def get_custom_emoji_stickers(
        self, custom_emoji_ids: list[str]
    ) -> Awaitable[Any]:
        """Get information about custom emoji stickers by their identifiers."""
        return self.api_call(
            "getCustomEmojiStickers", custom_emoji_ids=custom_emoji_ids
        )

    def upload_sticker_file(
        self,
        user_id: int,
        sticker: "TG_SendFileInput",
        sticker_format: Literal["static", "animated", "video"],
    ) -> Awaitable[Any]:
        """
        Upload a sticker file for later use in createNewStickerSet/addStickerToSet.

        :param int user_id: Owner of the uploaded file
        :param sticker: The sticker file itself
        :param sticker_format: "static", "animated" or "video"
        """
        return self.api_call(
            "uploadStickerFile",
            user_id=user_id,
            sticker=sticker,
            sticker_format=sticker_format,
        )

    def create_new_sticker_set(
        self,
        user_id: int,
        name: str,
        title: str,
        stickers: list[TG_InputSticker],
        **options: Unpack[TG_CreateNewStickerSetOpts],
    ) -> Awaitable[TG_BoolResponse]:
        """
        Create a new sticker set owned by a user.

        :param int user_id: User who will own the new sticker set
        :param str name: Short name, e.g. "cats_by_mybot"
        :param str title: Sticker set title
        :param stickers: 1-50 initial stickers
        :param options: Additional createNewStickerSet options (see
            https://core.telegram.org/bots/api#createnewstickerset)
        """
        return self.api_call(
            "createNewStickerSet",
            user_id=user_id,
            name=name,
            title=title,
            stickers=stickers,
            **options,
        )

    def add_sticker_to_set(
        self, user_id: int, name: str, sticker: TG_InputSticker
    ) -> Awaitable[TG_BoolResponse]:
        """
        Add a sticker to a set created by the bot. Max 50 stickers per regular
        or custom emoji set, 200 per mask set.

        :param int user_id: Sticker set owner
        :param str name: Sticker set name
        :param sticker: The sticker to add
        """
        return self.api_call(
            "addStickerToSet", user_id=user_id, name=name, sticker=sticker
        )

    def set_sticker_position_in_set(
        self, sticker: str, position: int
    ) -> Awaitable[TG_BoolResponse]:
        """Move a sticker in a set created by the bot to a specific position."""
        return self.api_call(
            "setStickerPositionInSet", sticker=sticker, position=position
        )

    def delete_sticker_from_set(self, sticker: str) -> Awaitable[TG_BoolResponse]:
        """Delete a sticker from a set created by the bot."""
        return self.api_call("deleteStickerFromSet", sticker=sticker)

    def replace_sticker_in_set(
        self, user_id: int, name: str, old_sticker: str, sticker: TG_InputSticker
    ) -> Awaitable[TG_BoolResponse]:
        """
        Replace an existing sticker in a set with a new one, keeping its position.

        :param int user_id: Sticker set owner
        :param str name: Sticker set name
        :param str old_sticker: file_id of the sticker to replace
        :param sticker: The replacement sticker
        """
        return self.api_call(
            "replaceStickerInSet",
            user_id=user_id,
            name=name,
            old_sticker=old_sticker,
            sticker=sticker,
        )

    def set_sticker_emoji_list(
        self, sticker: str, emoji_list: list[str]
    ) -> Awaitable[TG_BoolResponse]:
        """Change the emoji list associated with a sticker."""
        return self.api_call(
            "setStickerEmojiList", sticker=sticker, emoji_list=emoji_list
        )

    def set_sticker_keywords(
        self, sticker: str, keywords: list[str] | None = None
    ) -> Awaitable[TG_BoolResponse]:
        """Change search keywords associated with a sticker."""
        return self.api_call(
            "setStickerKeywords", sticker=sticker, keywords=keywords or []
        )

    def set_sticker_mask_position(
        self, sticker: str, mask_position: "TG_MaskPosition | None" = None
    ) -> Awaitable[TG_BoolResponse]:
        """Change the mask position of a mask sticker."""
        options: dict[str, Any] = (
            {"mask_position": mask_position} if mask_position else {}
        )
        return self.api_call("setStickerMaskPosition", sticker=sticker, **options)

    def set_sticker_set_title(
        self, name: str, title: str
    ) -> Awaitable[TG_BoolResponse]:
        """Set the title of a sticker set created by the bot."""
        return self.api_call("setStickerSetTitle", name=name, title=title)

    def set_sticker_set_thumbnail(
        self,
        name: str,
        user_id: int,
        sticker_format: Literal["static", "animated", "video"],
        thumbnail: "TG_SendFileInput | None" = None,
    ) -> Awaitable[TG_BoolResponse]:
        """
        Set the thumbnail of a regular or mask sticker set.

        :param str name: Sticker set name
        :param int user_id: Sticker set owner
        :param sticker_format: "static", "animated" or "video"
        :param thumbnail: New thumbnail, or None to drop it
        """
        options: dict[str, Any] = {"thumbnail": thumbnail} if thumbnail else {}
        return self.api_call(
            "setStickerSetThumbnail",
            name=name,
            user_id=user_id,
            format=sticker_format,
            **options,
        )

    def set_custom_emoji_sticker_set_thumbnail(
        self, name: str, custom_emoji_id: str = ""
    ) -> Awaitable[TG_BoolResponse]:
        """Set the thumbnail of a custom emoji sticker set."""
        return self.api_call(
            "setCustomEmojiStickerSetThumbnail",
            name=name,
            custom_emoji_id=custom_emoji_id,
        )

    def delete_sticker_set(self, name: str) -> Awaitable[TG_BoolResponse]:
        """Delete a sticker set created by the bot."""
        return self.api_call("deleteStickerSet", name=name)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_bot.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add aiotg/bot.py aiotg/types_.py tests/test_bot.py
git commit -m "feat: add sticker set management methods

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 8: Polls, dice, animation, video notes — methods, type completions, `MESSAGE_TYPES`

**Files:**
- Modify: `aiotg/chat.py` (insert after Task 4's methods — placing these near the other `send_*` methods, e.g. after `send_media_group`), `aiotg/bot.py:83-103` (`MESSAGE_TYPES`), `aiotg/types_.py` (replace 5 `= Any` stubs with real types, add 4 new `Opts` types)
- Test: `tests/test_chat.py`

**Interfaces:**
- Consumes: existing `TG_SendOpts`, `TG_SendFileInput`, `TG_MessageEntity`, `TG_InlineKeyboardMarkup`.
- Produces: `Chat.send_poll`, `.send_dice`, `.send_animation`, `.send_video_note`, `.stop_poll`; real `TG_Poll`, `TG_PollAnswer`, `TG_Dice`, `TG_Contact`, `TG_Venue`, `TG_Location` types (previously `Any`) used by `TG_Message`/`TG_ExternalReplyInfo` and by `handle("poll"|"dice"|"contact"|"venue"|"location")` callbacks.

**Naming gotcha:** Telegram's `sendPoll` field for the answer choices is literally called `options` — which collides with this codebase's `**options: Unpack[...]` convention. The method below names the parameter `poll_options` and forwards it as `options=poll_options` in the `api_call`.

- [ ] **Step 1: Replace 5 `Any` stubs with real types, add 4 new `Opts` types, and write the failing tests**

In `aiotg/types_.py`, the stub block (around line 77) currently reads:
```python
TG_Voice = Any
TG_PaidMedia = Any
TG_Checklist = Any
TG_Contact = Any
TG_Dice = Any
TG_Game = Any
TG_Giveaway = Any
TG_GiveawayWinners = Any
TG_Invoice = Any
TG_Location = Any
TG_Poll = Any
TG_Venue = Any
TG_TextQuote = Any
```
Replace it with (keeping the untouched names as-is, expanding the five in scope):
```python
TG_Voice = Any
TG_PaidMedia = Any
TG_Checklist = Any


class TG_Contact(TypedDict, total=False):
    phone_number: Required[str]
    first_name: Required[str]
    last_name: str
    user_id: int
    vcard: str


class TG_Dice(TypedDict, total=True):
    emoji: str
    value: int


TG_Game = Any
TG_Giveaway = Any
TG_GiveawayWinners = Any
TG_Invoice = Any


class TG_Location(TypedDict, total=False):
    longitude: Required[float]
    latitude: Required[float]
    horizontal_accuracy: float
    live_period: int
    heading: int
    proximity_alert_radius: int


class TG_PollOption(TypedDict, total=False):
    text: Required[str]
    voter_count: Required[int]
    text_entities: list["TG_MessageEntity"]


class TG_Poll(TypedDict, total=False):
    id: Required[str]
    question: Required[str]
    options: Required[list[TG_PollOption]]
    total_voter_count: Required[int]
    is_closed: Required[bool]
    is_anonymous: Required[bool]
    type: Required[Literal["regular", "quiz"]]
    allows_multiple_answers: Required[bool]
    correct_option_id: int
    explanation: str
    explanation_entities: list["TG_MessageEntity"]
    open_period: int
    close_date: int


class TG_Venue(TypedDict, total=False):
    location: Required[TG_Location]
    title: Required[str]
    address: Required[str]
    foursquare_id: str
    foursquare_type: str
    google_place_id: str
    google_place_type: str


TG_TextQuote = Any
```
(`TG_Poll`/`TG_PollOption` reference `"TG_MessageEntity"` as a quoted forward reference since that type isn't defined until later in the file — the same pattern `TG_ReplyParameters` already uses a few lines up.)

Further down the same stub block, replace the single line `TG_PollAnswer = Any` with:
```python
class TG_PollAnswer(TypedDict, total=False):
    poll_id: Required[str]
    voter_chat: "TG_Chat"
    user: "TG_User"
    option_ids: Required[list[int]]
```
(quoted forward refs to `TG_Chat`/`TG_User`, both defined later in the file.)

Add near `TG_SendVoiceOpts`:
```python
class TG_SendPollOpts(TG_SendOpts, total=False):
    question_parse_mode: str
    question_entities: list[TG_MessageEntity]
    is_anonymous: bool
    type: Literal["regular", "quiz"]
    allows_multiple_answers: bool
    correct_option_id: int
    explanation: str
    explanation_parse_mode: str
    explanation_entities: list[TG_MessageEntity]
    open_period: int
    close_date: int
    is_closed: bool


class TG_SendDiceOpts(TG_SendOpts, total=False):
    emoji: str


class TG_SendAnimationOpts(TG_SendOpts, total=False):
    duration: int
    width: int
    height: int
    thumbnail: TG_SendFileInput
    has_spoiler: bool
    show_caption_above_media: bool
    parse_mode: str
    caption_entities: list[TG_MessageEntity]


class TG_SendVideoNoteOpts(TG_SendOpts, total=False):
    duration: int
    length: int
    thumbnail: TG_SendFileInput
```

Add to `tests/test_chat.py`:
```python
def test_send_poll_dice_animation_video_note() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.send_poll("Cats or dogs?", ["Cats", "Dogs"])
    assert bot.calls["sendPoll"]["question"] == "Cats or dogs?"
    assert bot.calls["sendPoll"]["options"] == ["Cats", "Dogs"]

    chat.send_dice()
    assert "sendDice" in bot.calls

    chat.send_animation(b"foo")
    assert "sendAnimation" in bot.calls

    chat.send_video_note(b"foo")
    assert "sendVideoNote" in bot.calls

    chat.stop_poll(1337)
    assert bot.calls["stopPoll"]["message_id"] == 1337
```
(`"animation"`, `"dice"`, `"video_note"`, `"poll"` in `MESSAGE_TYPES` are already exercised by the existing parametrized `test_handle` in `tests/test_callbacks.py` — no new test needed there, just the list update in Step 3.)

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_chat.py -v -k send_poll_dice_animation_video_note`
Expected: FAIL — `AttributeError`

- [ ] **Step 3: Implement**

Add `TG_SendPollOpts`, `TG_SendDiceOpts`, `TG_SendAnimationOpts`, `TG_SendVideoNoteOpts` to `chat.py`'s type imports, then add to `Chat` (near `send_media_group`):
```python
    def send_poll(
        self,
        question: str,
        poll_options: list[str],
        **options: Unpack[TG_SendPollOpts],
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send a native poll.

        :param str question: Poll question, 1-300 characters
        :param poll_options: 2-12 answer options
        :param options: Additional sendPoll options (see
            https://core.telegram.org/bots/api#sendpoll)
        """
        return self.bot.api_call(
            "sendPoll",
            chat_id=str(self.id),
            question=question,
            options=poll_options,
            **options,
        )

    def send_dice(
        self, **options: Unpack[TG_SendDiceOpts]
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send an animated emoji that displays a random value (dice, dart, etc).

        :param options: Additional sendDice options, including emoji (see
            https://core.telegram.org/bots/api#senddice)
        """
        return self.bot.api_call("sendDice", chat_id=str(self.id), **options)

    def send_animation(
        self,
        animation: TG_SendFileInput,
        caption: str = "",
        **options: Unpack[TG_SendAnimationOpts],
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send an animation file (GIF or H.264/MPEG-4 AVC video without sound).

        :param animation: Object containing the animation data
        :param str caption: Animation caption (optional)
        :param options: Additional sendAnimation options (see
            https://core.telegram.org/bots/api#sendanimation)
        """
        return self.bot.api_call(
            "sendAnimation",
            chat_id=str(self.id),
            animation=animation,
            caption=caption,
            **options,
        )

    def send_video_note(
        self, video_note: TG_SendFileInput, **options: Unpack[TG_SendVideoNoteOpts]
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send a rounded square mp4 video without sound (video message).

        :param video_note: Object containing the video note data
        :param options: Additional sendVideoNote options (see
            https://core.telegram.org/bots/api#sendvideonote)
        """
        return self.bot.api_call(
            "sendVideoNote", chat_id=str(self.id), video_note=video_note, **options
        )

    def stop_poll(
        self, message_id: int, reply_markup: TG_InlineKeyboardMarkup | None = None
    ) -> Awaitable[Any]:
        """
        Stop a poll sent by the bot and return the final results.

        :param int message_id: Identifier of the original poll message
        :param dict reply_markup: New inline keyboard for the stopped message
        """
        options: dict[str, Any] = (
            {"reply_markup": reply_markup} if reply_markup else {}
        )
        return self.bot.api_call(
            "stopPoll", chat_id=self.id, message_id=message_id, **options
        )
```

In `aiotg/bot.py`, change `MESSAGE_TYPES` (lines 83-103) by adding four entries:
```python
MESSAGE_TYPES = [
    "location",
    "photo",
    "document",
    "audio",
    "voice",
    "sticker",
    "contact",
    "venue",
    "video",
    "game",
    "story",
    "animation",
    "dice",
    "video_note",
    "poll",
    "delete_chat_photo",
    "new_chat_photo",
    "new_chat_members",
    "new_chat_member",
    "left_chat_member",
    "new_chat_title",
    "group_chat_created",
    "successful_payment",
]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_chat.py tests/test_callbacks.py -v`
Expected: PASS (the parametrized `test_handle` in `test_callbacks.py` now also runs for the 4 new `MESSAGE_TYPES` entries)

- [ ] **Step 5: Commit**

```bash
git add aiotg/chat.py aiotg/bot.py aiotg/types_.py tests/test_chat.py
git commit -m "feat: add poll, dice, animation and video note methods; complete their types

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 9: Live location, caption/media editing, plural copy/forward/delete

**Files:**
- Modify: `aiotg/chat.py:417-431` (`forward_message`, upgraded — accurate only if Tasks 1-8 inserted methods after this point, not before; if line numbers don't match, locate by `def forward_message`), `aiotg/chat.py` (insert new methods after `edit_reply_markup`, originally line 117), `aiotg/types_.py` (`TG_ForwardMessageOpts` — locate by name, lines have shifted)
- Test: `tests/test_chat.py`

**Interfaces:**
- Consumes: existing `TG_InlineKeyboardMarkup`, `TG_SendOpts`, `TG_MessageResponse`, `TG_BoolResponse`.
- Produces: `Chat.edit_message_live_location`, `.stop_message_live_location`, `.edit_message_caption`, `.edit_message_media`, `.copy_message`, `.copy_messages`, `.forward_messages`, `.delete_messages`; `Chat.forward_message` now accepts `**options`.

- [ ] **Step 1: Fix `TG_ForwardMessageOpts`, add 4 new Opts types, and write the failing tests**

In `aiotg/types_.py`, replace:
```python
class TG_ForwardMessageOpts(TypedDict, total=False):
    chat_id: Required[str | int]
    message_thread_id: int
    direct_messages_topic_id: int
    from_chat_id: Required[str | int]
    video_start_timestamp: int
    disable_notification: bool
    protect_content: bool
    message_id: Required[int]
```
with:
```python
class TG_ForwardMessageOpts(TypedDict, total=False):
    message_thread_id: int
    direct_messages_topic_id: int
    video_start_timestamp: int
    disable_notification: bool
    protect_content: bool
```
(dropping the required fields, same fix pattern as Task 1-5. Reused as-is for `forward_messages`, the plural variant, rather than adding a near-duplicate type — `video_start_timestamp` is technically singular-only, low-risk over-permissiveness in exchange for one fewer type.)

Add near `TG_SendMessageOpts`:
```python
class TG_EditMessageLiveLocationOpts(TypedDict, total=False):
    business_connection_id: str
    live_period: int
    horizontal_accuracy: float
    heading: int
    proximity_alert_radius: int
    reply_markup: TG_InlineKeyboardMarkup


class TG_StopMessageLiveLocationOpts(TypedDict, total=False):
    business_connection_id: str
    reply_markup: TG_InlineKeyboardMarkup


class TG_EditMessageCaptionOpts(TypedDict, total=False):
    business_connection_id: str
    parse_mode: str
    caption_entities: list[TG_MessageEntity]
    show_caption_above_media: bool
    reply_markup: TG_InlineKeyboardMarkup


class TG_EditMessageMediaOpts(TypedDict, total=False):
    business_connection_id: str
    reply_markup: TG_InlineKeyboardMarkup


class TG_CopyMessageOpts(TG_SendOpts, total=False):
    caption: str
    parse_mode: str
    caption_entities: list[TG_MessageEntity]
    show_caption_above_media: bool


class TG_CopyMessagesOpts(TypedDict, total=False):
    message_thread_id: int
    disable_notification: bool
    protect_content: bool
    remove_caption: bool
```

Add to `tests/test_chat.py`:
```python
def test_edit_message_live_location_caption_and_media() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.edit_message_live_location(1337, 13.0, 37.0)
    assert bot.calls["editMessageLiveLocation"]["latitude"] == 13.0

    chat.stop_message_live_location(1337)
    assert bot.calls["stopMessageLiveLocation"]["message_id"] == 1337

    chat.edit_message_caption(1337, caption="new caption")
    assert bot.calls["editMessageCaption"]["caption"] == "new caption"

    chat.edit_message_media(1337, {"type": "photo", "media": "file_id"})
    assert bot.calls["editMessageMedia"]["media"] == {"type": "photo", "media": "file_id"}


def test_copy_forward_and_delete_messages() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.forward_message(99, 5, disable_notification=True)
    assert bot.calls["forwardMessage"]["message_id"] == 5
    assert bot.calls["forwardMessage"]["disable_notification"] is True

    chat.copy_message(99, 5)
    assert bot.calls["copyMessage"]["message_id"] == 5

    chat.copy_messages(99, [5, 6])
    assert bot.calls["copyMessages"]["message_ids"] == [5, 6]

    chat.forward_messages(99, [5, 6])
    assert bot.calls["forwardMessages"]["message_ids"] == [5, 6]

    chat.delete_messages([5, 6])
    assert bot.calls["deleteMessages"]["message_ids"] == [5, 6]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_chat.py -v -k "live_location or copy_forward_and_delete"`
Expected: FAIL — `TypeError` on `forward_message` (new kwarg), `AttributeError` on the rest

- [ ] **Step 3: Implement**

Add the 6 new type names to `chat.py`'s type imports, then replace `forward_message` (lines 417-431) with:
```python
    def forward_message(
        self,
        from_chat_id: int,
        message_id: int,
        **options: Unpack[TG_ForwardMessageOpts],
    ) -> Awaitable[TG_MessageResponse]:
        """
        Forward a message from another chat to this chat.

        :param int from_chat_id: ID of the chat to forward the message from
        :param int message_id: ID of the message to forward
        :param options: Additional forwardMessage options (see
            https://core.telegram.org/bots/api#forwardmessage)
        """
        return self.bot.api_call(
            "forwardMessage",
            chat_id=self.id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            **options,
        )
```

Add after `edit_reply_markup` (line 117):
```python
    def edit_message_live_location(
        self,
        message_id: int,
        latitude: float,
        longitude: float,
        **options: Unpack[TG_EditMessageLiveLocationOpts],
    ) -> Awaitable[Any]:
        """
        Update the live location of a message sent by the bot.

        :param int message_id: Identifier of the message to edit
        :param float latitude: New latitude
        :param float longitude: New longitude
        :param options: Additional editMessageLiveLocation options (see
            https://core.telegram.org/bots/api#editmessagelivelocation)
        """
        return self.bot.api_call(
            "editMessageLiveLocation",
            chat_id=self.id,
            message_id=message_id,
            latitude=latitude,
            longitude=longitude,
            **options,
        )

    def stop_message_live_location(
        self, message_id: int, **options: Unpack[TG_StopMessageLiveLocationOpts]
    ) -> Awaitable[Any]:
        """
        Stop updating a live location message before live_period expires.

        :param int message_id: Identifier of the message to stop
        :param options: Additional stopMessageLiveLocation options (see
            https://core.telegram.org/bots/api#stopmessagelivelocation)
        """
        return self.bot.api_call(
            "stopMessageLiveLocation", chat_id=self.id, message_id=message_id, **options
        )

    def edit_message_caption(
        self,
        message_id: int,
        caption: str = "",
        **options: Unpack[TG_EditMessageCaptionOpts],
    ) -> Awaitable[TG_MessageResponse]:
        """
        Edit the caption of a message sent by the bot.

        :param int message_id: Identifier of the message to edit
        :param str caption: New caption
        :param options: Additional editMessageCaption options (see
            https://core.telegram.org/bots/api#editmessagecaption)
        """
        return self.bot.api_call(
            "editMessageCaption",
            chat_id=self.id,
            message_id=message_id,
            caption=caption,
            **options,
        )

    def edit_message_media(
        self,
        message_id: int,
        media: dict[str, Any],
        **options: Unpack[TG_EditMessageMediaOpts],
    ) -> Awaitable[TG_MessageResponse]:
        """
        Edit the media (photo/video/document/audio/animation) of a message
        sent by the bot.

        :param int message_id: Identifier of the message to edit
        :param media: A serialized InputMedia object describing the new media
            (see https://core.telegram.org/bots/api#inputmedia)
        :param options: Additional editMessageMedia options (see
            https://core.telegram.org/bots/api#editmessagemedia)
        """
        # ponytail: media typed as dict[str, Any] rather than the full
        # InputMedia union (7 variants) — model properly if callers need
        # static checking per media kind
        return self.bot.api_call(
            "editMessageMedia",
            chat_id=self.id,
            message_id=message_id,
            media=media,
            **options,
        )

    def copy_message(
        self,
        from_chat_id: int | str,
        message_id: int,
        **options: Unpack[TG_CopyMessageOpts],
    ) -> Awaitable[Any]:
        """
        Copy a message (no "Forwarded from" link) into this chat.

        :param from_chat_id: ID of the chat the message is copied from
        :param int message_id: Identifier of the message to copy
        :param options: Additional copyMessage options (see
            https://core.telegram.org/bots/api#copymessage)
        """
        return self.bot.api_call(
            "copyMessage",
            chat_id=self.id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            **options,
        )

    def copy_messages(
        self,
        from_chat_id: int | str,
        message_ids: list[int],
        **options: Unpack[TG_CopyMessagesOpts],
    ) -> Awaitable[Any]:
        """
        Copy 1-100 messages (no "Forwarded from" link) into this chat.

        :param from_chat_id: ID of the chat the messages are copied from
        :param message_ids: Identifiers of the messages to copy
        :param options: Additional copyMessages options (see
            https://core.telegram.org/bots/api#copymessages)
        """
        return self.bot.api_call(
            "copyMessages",
            chat_id=self.id,
            from_chat_id=from_chat_id,
            message_ids=message_ids,
            **options,
        )

    def forward_messages(
        self,
        from_chat_id: int | str,
        message_ids: list[int],
        **options: Unpack[TG_ForwardMessageOpts],
    ) -> Awaitable[Any]:
        """
        Forward 1-100 messages into this chat.

        :param from_chat_id: ID of the chat the messages are forwarded from
        :param message_ids: Identifiers of the messages to forward
        :param options: Additional forwardMessages options (see
            https://core.telegram.org/bots/api#forwardmessages)
        """
        return self.bot.api_call(
            "forwardMessages",
            chat_id=self.id,
            from_chat_id=from_chat_id,
            message_ids=message_ids,
            **options,
        )

    def delete_messages(self, message_ids: list[int]) -> Awaitable[TG_BoolResponse]:
        """
        Delete multiple messages from this chat at once.

        :param message_ids: Identifiers of the messages to delete, 1-100
        """
        return self.bot.api_call(
            "deleteMessages", chat_id=self.id, message_ids=message_ids
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_chat.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add aiotg/chat.py aiotg/types_.py tests/test_chat.py
git commit -m "feat: add live location, caption/media editing, and plural copy/forward/delete

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 10: Message reactions

**Files:**
- Modify: `aiotg/chat.py` (insert after Task 9's methods), `aiotg/types_.py` (new `TG_ReactionType`, near `TG_MessageEntity`)
- Test: `tests/test_chat.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `Chat.set_message_reaction`; `TG_ReactionType`, reused by Task 11's `TG_MessageReactionUpdated`/`TG_MessageReactionCountUpdated`.

- [ ] **Step 1: Add `TG_ReactionType` and write the failing test**

Add to `aiotg/types_.py` (near `TG_MessageEntity`):
```python
TG_ReactionType = TypedDict(
    "TG_ReactionType",
    {
        "type": Required[Literal["emoji", "custom_emoji"]],
        "emoji": NotRequired[str],
        "custom_emoji_id": NotRequired[str],
    },
    total=True,
)
```

Add to `tests/test_chat.py`:
```python
def test_set_message_reaction() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.set_message_reaction(1337, [{"type": "emoji", "emoji": "\U0001F44D"}])
    assert bot.calls["setMessageReaction"]["message_id"] == 1337
    assert bot.calls["setMessageReaction"]["reaction"] == [
        {"type": "emoji", "emoji": "\U0001F44D"}
    ]

    chat.set_message_reaction(1338)
    assert bot.calls["setMessageReaction"]["reaction"] == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_chat.py -v -k set_message_reaction`
Expected: FAIL — `AttributeError`

- [ ] **Step 3: Implement**

Add `TG_ReactionType` to `chat.py`'s type imports, then add to `Chat`:
```python
    def set_message_reaction(
        self,
        message_id: int,
        reaction: list[TG_ReactionType] | None = None,
        is_big: bool = False,
    ) -> Awaitable[TG_BoolResponse]:
        """
        Set the bot's reaction on a message. An empty reaction list removes
        the bot's current reaction.

        :param int message_id: Identifier of the target message
        :param reaction: New list of reactions (see
            https://core.telegram.org/bots/api#setmessagereaction)
        :param bool is_big: Whether to show a big single reaction animation
        """
        return self.bot.api_call(
            "setMessageReaction",
            chat_id=self.id,
            message_id=message_id,
            reaction=reaction or [],
            is_big=is_big,
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_chat.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add aiotg/chat.py aiotg/types_.py tests/test_chat.py
git commit -m "feat: add set_message_reaction

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 11: Misc Bot methods (`get_webhook_info`, `close`, `log_out`)

**Files:**
- Modify: `aiotg/bot.py` (insert after `delete_webhook` — originally line 731, but Tasks 5-7 add substantial content to `bot.py` before this point runs; locate by `def delete_webhook`)
- Test: `tests/test_bot.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `Bot.get_webhook_info`, `Bot.close`, `Bot.log_out`.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_bot.py`:
```python
def test_webhook_info_close_and_log_out() -> None:
    bot = MockBot()

    bot.get_webhook_info()
    assert "getWebhookInfo" in bot.calls

    bot.close()
    assert "close" in bot.calls

    bot.log_out()
    assert "logOut" in bot.calls
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_bot.py -v -k webhook_info_close_and_log_out`
Expected: FAIL — `AttributeError`

- [ ] **Step 3: Implement**

Add to `Bot` (after `delete_webhook`, line 731):
```python
    def get_webhook_info(self) -> Awaitable[Any]:
        """
        Get current webhook status. Returns an object with url set to an
        empty string if the bot is using getUpdates instead.
        """
        return self.api_call("getWebhookInfo")

    def close(self) -> Awaitable[TG_BoolResponse]:
        """
        Close the bot instance before moving it from one local Bot API
        server to another. Distinct from closing the aiohttp session (see
        Bot.session / loop.run_until_complete(self.session.close())).
        """
        return self.api_call("close")

    def log_out(self) -> Awaitable[TG_BoolResponse]:
        """
        Log out from the cloud Bot API server before launching the bot
        locally. Not supported when running the bot against a local server.
        """
        return self.api_call("logOut")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_bot.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add aiotg/bot.py tests/test_bot.py
git commit -m "feat: add get_webhook_info, close and log_out

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Task 12: Inbound update handlers (poll, poll_answer, chat member/boost/reaction updates, join requests)

**Files:**
- Modify: `aiotg/bot.py` (all line numbers below are from the *original* file; by Task 12, Tasks 5/6/7/11 have added ~400+ lines to `bot.py`, so locate every target by name, not line number): new `Default*Handler` type aliases near the others (originally lines 39-116), `Bot.__init__` (originally lines 135-178), new decorator methods near `not_handled_update` (originally line 337), `_process_update` (originally lines 821-851); `aiotg/types_.py` (6 more `= Any` stubs replaced, locate by name)
- Test: `tests/test_callbacks.py`

**Interfaces:**
- Consumes: `TG_ReactionType` (from Task 10).
- Produces: `Bot.poll`, `.poll_answer`, `.my_chat_member`, `.chat_member`, `.chat_join_request`, `.chat_boost`, `.removed_chat_boost`, `.message_reaction`, `.message_reaction_count` decorators; real `TG_ChatJoinRequest`, `TG_ChatBoostUpdated`, `TG_ChatBoostRemoved`, `TG_ChatMemberUpdated`, `TG_MessageReactionUpdated`, `TG_MessageReactionCountUpdated` types.

- [ ] **Step 1: Replace 6 more `Any` stubs with real types, fix a test fixture this task invalidates, and write the failing test**

`tests/test_callbacks.py::test_not_handled_update` currently uses `{"update_id": 0, "poll": {}}` as its example of a genuinely-unhandled update. Once this task adds the `poll` branch, that update becomes handled, and the existing test would start failing for the wrong reason. Change its fixture to a key nothing will ever handle:
```python
    update = cast(TG_Update, cast(object, {"update_id": 0, "some_future_update_type": {}}))
```
(replacing the existing `update = cast(TG_Update, cast(object, {"update_id": 0, "poll": {}}))` line — the two `log.check(...)` assertions and `assert called_with == update` stay as they are.)

In `aiotg/types_.py`, the stub block has this run (locate via `TG_MessageReactionUpdated = Any`):
```python
TG_MessageReactionUpdated = Any
TG_MessageReactionCountUpdated = Any
TG_ShippingQuery = Any
TG_PaidMediaPurchaed = Any
```
Replace the first two lines (leave `TG_ShippingQuery`/`TG_PaidMediaPurchaed` as `Any` — out of scope, Payments was cut) with:
```python
class TG_ReactionCount(TypedDict, total=True):
    type: "TG_ReactionType"
    total_count: int


TG_MessageReactionUpdated = TypedDict(
    "TG_MessageReactionUpdated",
    {
        "chat": Required["TG_Chat"],
        "message_id": Required[int],
        "user": NotRequired["TG_User"],
        "actor_chat": NotRequired["TG_Chat"],
        "date": Required[int],
        "old_reaction": Required[list["TG_ReactionType"]],
        "new_reaction": Required[list["TG_ReactionType"]],
    },
    total=True,
)


class TG_MessageReactionCountUpdated(TypedDict, total=True):
    chat: "TG_Chat"
    message_id: int
    date: int
    reactions: list[TG_ReactionCount]


TG_ShippingQuery = Any
TG_PaidMediaPurchaed = Any
```

A little further down the same block (locate via `TG_ChatMemberUpdated = Any`):
```python
TG_ChatMemberUpdated = Any
TG_ChatJoinRequest = Any
TG_ChatBoostUpdated = Any
TG_ChatBoostRemoved = Any
```
Replace with:
```python
TG_ChatMemberUpdated = TypedDict(
    "TG_ChatMemberUpdated",
    {
        "chat": Required["TG_Chat"],
        "from": Required["TG_User"],
        "date": Required[int],
        "old_chat_member": Required["TG_ChatMember"],
        "new_chat_member": Required["TG_ChatMember"],
        "invite_link": NotRequired["TG_ChatInviteLink"],
        "via_join_request": NotRequired[bool],
        "via_chat_folder_invite_link": NotRequired[bool],
    },
    total=True,
)

TG_ChatJoinRequest = TypedDict(
    "TG_ChatJoinRequest",
    {
        "chat": Required["TG_Chat"],
        "from": Required["TG_User"],
        "user_chat_id": Required[int],
        "date": Required[int],
        "bio": NotRequired[str],
        "invite_link": NotRequired["TG_ChatInviteLink"],
    },
    total=True,
)


class TG_ChatBoost(TypedDict, total=False):
    boost_id: Required[str]
    add_date: Required[int]
    expiration_date: Required[int]
    source: Required[Any]  # ChatBoostSource union — see Global Constraints


class TG_ChatBoostUpdated(TypedDict, total=True):
    chat: "TG_Chat"
    boost: TG_ChatBoost


class TG_ChatBoostRemoved(TypedDict, total=False):
    chat: Required["TG_Chat"]
    boost_id: Required[str]
    remove_date: Required[int]
    source: Required[Any]
```
(`TG_ChatMember`, `TG_ChatInviteLink`, `TG_Chat`, `TG_User` are all defined later in the file than this stub block, hence the quoted forward references — same pattern used throughout `TG_Message`.)

Add to `tests/test_callbacks.py`:
```python
NEW_UPDATE_HANDLERS = [
    "poll",
    "poll_answer",
    "my_chat_member",
    "chat_member",
    "chat_join_request",
    "chat_boost",
    "removed_chat_boost",
    "message_reaction",
    "message_reaction_count",
]


@pytest.mark.parametrize("upd_type", NEW_UPDATE_HANDLERS)
def test_new_update_handlers(upd_type: str) -> None:
    called_with: Any = None

    def _(payload: Any) -> None:
        nonlocal called_with
        called_with = payload

    getattr(bot, upd_type)(_)

    payload = {"marker": upd_type}
    update = cast(TG_Update, cast(object, {"update_id": 0, upd_type: payload}))
    bot._process_update(update)
    assert called_with == payload
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_callbacks.py -v -k test_new_update_handlers`
Expected: FAIL — `AttributeError: 'Bot' object has no attribute 'poll'`

- [ ] **Step 3: Implement**

In `aiotg/bot.py`, add near the other `Default*Handler` type aliases (after `DefaultNotHandledUpdateHandler`, around line 75):
```python
DefaultPollHandler = Callable[["TG_Poll"], Any]
DefaultPollAnswerHandler = Callable[["TG_PollAnswer"], Any]
DefaultMyChatMemberHandler = Callable[["TG_ChatMemberUpdated"], Any]
DefaultChatMemberHandler = Callable[["TG_ChatMemberUpdated"], Any]
DefaultChatJoinRequestHandler = Callable[["TG_ChatJoinRequest"], Any]
DefaultChatBoostHandler = Callable[["TG_ChatBoostUpdated"], Any]
DefaultRemovedChatBoostHandler = Callable[["TG_ChatBoostRemoved"], Any]
DefaultMessageReactionHandler = Callable[["TG_MessageReactionUpdated"], Any]
DefaultMessageReactionCountHandler = Callable[["TG_MessageReactionCountUpdated"], Any]
```

Add the 9 new type names to the `from .types_ import (...)` block. In `Bot.__init__`, add after `self._default_not_handled_update = (...)` (line 178):
```python
        self._default_poll: DefaultPollHandler = lambda poll: None
        self._default_poll_answer: DefaultPollAnswerHandler = lambda answer: None
        self._default_my_chat_member: DefaultMyChatMemberHandler = lambda cmu: None
        self._default_chat_member: DefaultChatMemberHandler = lambda cmu: None
        self._default_chat_join_request: DefaultChatJoinRequestHandler = (
            lambda req: None
        )
        self._default_chat_boost: DefaultChatBoostHandler = lambda boost: None
        self._default_removed_chat_boost: DefaultRemovedChatBoostHandler = (
            lambda boost: None
        )
        self._default_message_reaction: DefaultMessageReactionHandler = (
            lambda r: None
        )
        self._default_message_reaction_count: DefaultMessageReactionCountHandler = (
            lambda r: None
        )
```

Add decorator methods after `not_handled_update` (line 337):
```python
    def poll(self, callback: DefaultPollHandler) -> DefaultPollHandler:
        """
        Set callback for incoming poll updates (state changes of an
        anonymous poll the bot sent).
        """
        self._default_poll = callback
        return callback

    def poll_answer(
        self, callback: DefaultPollAnswerHandler
    ) -> DefaultPollAnswerHandler:
        """Set callback for poll_answer updates (a user's vote changed)."""
        self._default_poll_answer = callback
        return callback

    def my_chat_member(
        self, callback: DefaultMyChatMemberHandler
    ) -> DefaultMyChatMemberHandler:
        """Set callback for changes to the bot's own status in a chat."""
        self._default_my_chat_member = callback
        return callback

    def chat_member(
        self, callback: DefaultChatMemberHandler
    ) -> DefaultChatMemberHandler:
        """
        Set callback for other chat members' status changes. Requires
        explicitly listing "chat_member" in allowed_updates.
        """
        self._default_chat_member = callback
        return callback

    def chat_join_request(
        self, callback: DefaultChatJoinRequestHandler
    ) -> DefaultChatJoinRequestHandler:
        """Set callback for chat join requests."""
        self._default_chat_join_request = callback
        return callback

    def chat_boost(self, callback: DefaultChatBoostHandler) -> DefaultChatBoostHandler:
        """Set callback for a chat boost being added or changed."""
        self._default_chat_boost = callback
        return callback

    def removed_chat_boost(
        self, callback: DefaultRemovedChatBoostHandler
    ) -> DefaultRemovedChatBoostHandler:
        """Set callback for a chat boost being removed."""
        self._default_removed_chat_boost = callback
        return callback

    def message_reaction(
        self, callback: DefaultMessageReactionHandler
    ) -> DefaultMessageReactionHandler:
        """
        Set callback for a user's reaction on a message changing. Requires
        explicitly listing "message_reaction" in allowed_updates.
        """
        self._default_message_reaction = callback
        return callback

    def message_reaction_count(
        self, callback: DefaultMessageReactionCountHandler
    ) -> DefaultMessageReactionCountHandler:
        """Set callback for anonymized reaction count updates on a message."""
        self._default_message_reaction_count = callback
        return callback
```

In `_process_update` (lines 821-851), change the inner `if/elif/else` chain from:
```python
        else:
            if "inline_query" in update:
                coro = self._process_inline_query(update["inline_query"])
            elif "callback_query" in update:
                coro = self._process_callback_query(update["callback_query"])
            elif "pre_checkout_query" in update:
                coro = self._process_pre_checkout_query(update["pre_checkout_query"])
            elif "chosen_inline_result" in update:
                coro = self._process_chosen_inline_result(
                    update["chosen_inline_result"]
                )
            else:
                coro = self._process_not_handled_update(update)
                logger.error("don't know how to handle update: %s", update)
```
to:
```python
        else:
            if "inline_query" in update:
                coro = self._process_inline_query(update["inline_query"])
            elif "callback_query" in update:
                coro = self._process_callback_query(update["callback_query"])
            elif "pre_checkout_query" in update:
                coro = self._process_pre_checkout_query(update["pre_checkout_query"])
            elif "chosen_inline_result" in update:
                coro = self._process_chosen_inline_result(
                    update["chosen_inline_result"]
                )
            elif "poll" in update:
                coro = self._default_poll(update["poll"])
            elif "poll_answer" in update:
                coro = self._default_poll_answer(update["poll_answer"])
            elif "my_chat_member" in update:
                coro = self._default_my_chat_member(update["my_chat_member"])
            elif "chat_member" in update:
                coro = self._default_chat_member(update["chat_member"])
            elif "chat_join_request" in update:
                coro = self._default_chat_join_request(update["chat_join_request"])
            elif "chat_boost" in update:
                coro = self._default_chat_boost(update["chat_boost"])
            elif "removed_chat_boost" in update:
                coro = self._default_removed_chat_boost(update["removed_chat_boost"])
            elif "message_reaction" in update:
                coro = self._default_message_reaction(update["message_reaction"])
            elif "message_reaction_count" in update:
                coro = self._default_message_reaction_count(
                    update["message_reaction_count"]
                )
            else:
                coro = self._process_not_handled_update(update)
                logger.error("don't know how to handle update: %s", update)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_callbacks.py -v`
Expected: PASS (including the updated `test_not_handled_update`)

- [ ] **Step 5: Commit**

```bash
git add aiotg/bot.py aiotg/types_.py tests/test_callbacks.py
git commit -m "feat: dispatch poll, chat member, chat boost and reaction updates

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```
