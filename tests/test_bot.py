from aiotg.mock import MockBot


def test_get_forum_topic_icon_stickers() -> None:
    bot = MockBot()

    bot.get_forum_topic_icon_stickers()
    assert "getForumTopicIconStickers" in bot.calls
