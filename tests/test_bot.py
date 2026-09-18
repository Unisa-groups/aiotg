from aiotg.mock import MockBot


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
