from aiotg.mock import MockBot
from aiotg.types_ import TG_InputSticker


def test_get_forum_topic_icon_stickers() -> None:
    bot = MockBot()

    bot.get_forum_topic_icon_stickers()
    assert "getForumTopicIconStickers" in bot.calls


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


def test_sticker_set_management() -> None:
    bot = MockBot()
    sticker: TG_InputSticker = {
        "sticker": b"foo",
        "format": "static",
        "emoji_list": ["\U0001f600"],
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

    bot.set_sticker_emoji_list("CAAA", ["\U0001f600"])
    assert bot.calls["setStickerEmojiList"]["emoji_list"] == ["\U0001f600"]

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
