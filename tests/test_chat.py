from aiotg import Bot, Chat
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
