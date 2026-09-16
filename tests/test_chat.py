from aiotg import Bot, Chat
from aiotg.mock import MockBot
from aiotg.types_ import TG_Message

bot = Bot("test_token")


def _msg(extra: dict) -> TG_Message:
    base: TG_Message = {
        "message_id": 1,
        "chat": {"id": -100, "type": "supergroup"},
        "date": 0,
    }
    base.update(extra)
    return base


def test_sender_from_user() -> None:
    chat = Chat.from_message(bot, _msg({"from": {"first_name": "John", "id": 123}}))
    assert chat.sender["id"] == 123
    assert repr(chat.sender) == "John"


def test_sender_falls_back_to_sender_chat() -> None:
    # anonymous admin / channel auto-forward: no "from", but "sender_chat" has the id
    chat = Chat.from_message(
        bot,
        _msg(
            {"sender_chat": {"id": -100, "type": "supergroup", "title": "Unisa Group"}}
        ),
    )
    assert chat.sender["id"] == -100
    assert repr(chat.sender) == "Unisa Group"


def test_sender_missing_entirely() -> None:
    chat = Chat.from_message(bot, _msg({}))
    assert chat.sender.get("id") is None
    assert repr(chat.sender) == "N/A"


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
    assert bot.calls["setChatPermissions"]["permissions"] == {"can_send_messages": True}


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
    assert (
        bot.calls["revokeChatInviteLink"]["invite_link"] == "https://t.me/joinchat/abc"
    )


def test_chat_join_requests() -> None:
    bot = MockBot()
    chat = Chat(bot, 42)

    chat.approve_chat_join_request(7)
    assert bot.calls["approveChatJoinRequest"]["user_id"] == 7

    chat.decline_chat_join_request(7)
    assert bot.calls["declineChatJoinRequest"]["user_id"] == 7


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
