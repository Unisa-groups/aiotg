import aiohttp
import asyncio
import logging
import re
from .chat import Chat as Chat, Sender as Sender
from .reloader import run_with_reloader as run_with_reloader
from .types_ import (
    TG_CallbackQueryOpts as TG_CallbackQueryOpts,
    TG_CallbackQuerySrc as TG_CallbackQuerySrc,
    TG_ChosenInlineResultSrc as TG_ChosenInlineResultSrc,
    TG_EditMessageReplyMarkupOpts as TG_EditMessageReplyMarkupOpts,
    TG_EditMessageTextOpts as TG_EditMessageTextOpts,
    TG_File as TG_File,
    TG_GetUserProfilePhotosOpts as TG_GetUserProfilePhotosOpts,
    TG_InlineQueryAnswerOpts as TG_InlineQueryAnswerOpts,
    TG_InlineQueryResult as TG_InlineQueryResult,
    TG_InlineQuerySrc as TG_InlineQuerySrc,
    TG_Location as TG_Location,
    TG_Message as TG_Message,
    TG_MessageResponse as TG_MessageResponse,
    TG_PreCheckoutQuerySrc as TG_PreCheckoutQuerySrc,
    TG_SendMessageOpts as TG_SendMessageOpts,
    TG_SetWebhookOpts as TG_SetWebhookOpts,
    TG_Update as TG_Update,
    TG_UpdateResponse as TG_UpdateResponse,
    TG_User as TG_User,
)
from aiohttp import ClientResponse as ClientResponse, web
from aiohttp.client import _RequestContextManager
from collections.abc import Awaitable
from typing import Any, Callable, Unpack, overload

CommandHandler = Callable[["Chat", re.Match[str]], Any]
CommandDecorator = Callable[[CommandHandler], CommandHandler]
DefaultHandler = Callable[["Chat", "TG_Message"], Any]
DefaultInlineHandler = Callable[["InlineQuery"], Any]
RegexInlineHandler = Callable[["InlineQuery", re.Match[str]], Any]
RegexInlineDecorator = Callable[[RegexInlineHandler], RegexInlineHandler]
DefaultChosenInlineResultHandler = Callable[["ChosenInlineResult"], Any]
RegexChosenInlineResultHandler = Callable[["ChosenInlineResult", re.Match[str]], Any]
RegexChosenInlineResultDecorator = Callable[
    [RegexChosenInlineResultHandler], RegexChosenInlineResultHandler
]
DefaultCallbackHandler = Callable[["Chat | None", "CallbackQuery"], Any]
RegexCallbackHandler = Callable[["Chat | None", "CallbackQuery", re.Match[str]], Any]
RegexCallbackDecorator = Callable[[RegexCallbackHandler], RegexCallbackHandler]
DefaultCheckoutHandler = Callable[["PreCheckoutQuery"], Any]
RegexCheckoutHandler = Callable[["PreCheckoutQuery", re.Match[str]], Any]
RegexCheckoutDecorator = Callable[[RegexCheckoutHandler], RegexCheckoutHandler]
MessageHandler = Callable[["Chat", Any], Any]
MessageHandlerDecorator = Callable[[MessageHandler], MessageHandler]
API_URL: str
API_TIMEOUT: int
RETRY_TIMEOUT: int
RETRY_CODES: list[int]
MESSAGE_TYPES: list[str]
MESSAGE_UPDATES: list[str]
logger: logging.Logger

class Bot:
    """Telegram bot framework designed for asyncio

    :param str api_token: Telegram bot token, ask @BotFather for this
    :param int api_timeout: Timeout for long polling
    :param str name: Bot name
    :param callable json_serialize: JSON serializer function. (json.dumps by default)
    :param callable json_deserialize: JSON deserializer function. (json.loads by default)
    :param bool default_in_groups: Enables default callback in groups
    :param str proxy: Proxy URL to use for HTTP requests
    :param connector: Custom aiohttp connector
    """

    api_token: str
    api_timeout: int
    name: str | None
    json_serialize: Callable[..., str]
    json_deserialize: Callable[..., Any]
    default_in_groups: bool
    def __init__(
        self,
        api_token: str,
        api_timeout: int = ...,
        name: str | None = None,
        json_serialize: Callable[..., str] = ...,
        json_deserialize: Callable[..., Any] = ...,
        default_in_groups: bool = False,
        connector: aiohttp.BaseConnector | None = None,
    ) -> None: ...
    async def loop(self) -> None:
        """
        Return bot's main loop as coroutine. Use with asyncio.

        :Example:

        >>> loop = asyncio.get_event_loop()
        >>> loop.run_until_complete(bot.loop())

        or

        >>> loop = asyncio.get_event_loop()
        >>> loop.create_task(bot.loop())
        """
    def run(self, debug: bool = False, reload: bool | None = None) -> None:
        """
        Convenience method for running bots in getUpdates mode

        :param bool debug: Enable debug logging and automatic reloading
        :param bool reload: Automatically reload bot on code change
        :Example:

        >>> if __name__ == '__main__':
        >>>     bot.run()

        """
    def run_webhook(
        self, webhook_url: str, **options: Unpack[TG_SetWebhookOpts]
    ) -> None:
        """
        Convenience method for running bots in webhook mode

        :Example:

        >>> if __name__ == \'__main__\':
        >>>     bot.run_webhook(webhook_url="https://yourserver.com/webhooktoken")

        Additional documentation on https://core.telegram.org/bots/api#setwebhook
        """
    def stop_webhook(self) -> None:
        """
        Use to switch from Webhook to getUpdates mode
        """
    def add_command(self, regexp: str, fn: CommandHandler) -> None:
        """
        Manually register regexp based command
        """
    def command(self, regexp: str) -> CommandDecorator:
        """
        Register a new command

        :param str regexp: Regular expression matching the command to register

        :Example:

        >>> @bot.command(r"/echo (.+)")
        >>> def echo(chat, match):
        >>>     return chat.reply(match.group(1))
        """
    def default(self, callback: DefaultHandler) -> DefaultHandler:
        """
        Set callback for default command that is called on unrecognized
        commands for 1-to-1 chats
        If default_in_groups option is True, callback is called in groups too

        :Example:

        >>> @bot.default
        >>> def echo(chat, message):
        >>>     return chat.reply(message["text"])
        """
    def add_inline(self, regexp: str, fn: RegexInlineHandler) -> None:
        """
        Manually register regexp based callback
        """
    @overload
    def inline(self, callback: DefaultInlineHandler) -> DefaultInlineHandler: ...
    @overload
    def inline(self, callback: str) -> RegexInlineDecorator: ...
    def add_chosen_inline_result_callback(
        self, regexp: str, fn: RegexChosenInlineResultHandler
    ) -> None:
        """
        Manually register regexp based callback for the ``chosen_inline_result`` updates
        """
    @overload
    def chosen_inline_result_callback(
        self, callback: DefaultChosenInlineResultHandler
    ) -> DefaultChosenInlineResultHandler: ...
    @overload
    def chosen_inline_result_callback(
        self, callback: str
    ) -> RegexChosenInlineResultDecorator: ...
    def add_callback(self, regexp: str, fn: RegexCallbackHandler) -> None:
        """
        Manually register regexp based callback
        """
    @overload
    def callback(self, callback: DefaultCallbackHandler) -> DefaultCallbackHandler: ...
    @overload
    def callback(self, callback: str) -> RegexCallbackDecorator: ...
    def add_checkout(self, regexp: str, fn: RegexCheckoutHandler) -> None:
        """
        Manually register regexp based checkout handler
        """
    @overload
    def checkout(self, callback: DefaultCheckoutHandler) -> DefaultCheckoutHandler: ...
    @overload
    def checkout(self, callback: str) -> RegexCheckoutDecorator: ...
    def handle(self, msg_type: str) -> MessageHandlerDecorator:
        """
        Set handler for specific message type

        :Example:

        >>> @bot.handle("audio")
        >>> def handle(chat, audio):
        >>>     pass
        """
    def channel(self, channel_name: str) -> Chat:
        """
        Construct a Chat object used to post to channel

        :param str channel_name: Channel name
        """
    def private(self, user_id: str) -> Chat:
        """
        Construct a Chat object used to post direct messages

        :param str user_id: User id
        """
    def group(self, group_id: str) -> Chat:
        """
        Construct a Chat object used to post group messages

        :param str group_id: Group chat id
        """
    def api_call(self, method: str, **params: Any) -> Awaitable[Any]:
        """
        Call Telegram API.

        See https://core.telegram.org/bots/api for reference.

        :param str method: Telegram API method
        :param params: Arguments for the method call
        """
    async def get_me(self) -> TG_User:
        """
        Returns basic information about the bot
        (see https://core.telegram.org/bots/api#getme)
        """
    async def leave_chat(self, chat_id: int | str) -> bool:
        """
        Use this method for your bot to leave a group, supergroup or channel.
        Returns True on success.

        :param int chat_id: Unique identifier for the target chat             or username of the target supergroup or channel             (in the format @channelusername)
        """
    def send_message(
        self, chat_id: int | str, text: str, **options: Unpack[TG_SendMessageOpts]
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send a text message to chat

        :param int chat_id: ID of the chat to send the message to
        :param str text: Text to send
        :param options: Additional sendMessage options
            (see https://core.telegram.org/bots/api#sendmessage)
        """
    def edit_message_text(
        self,
        chat_id: int | str,
        message_id: int,
        text: str,
        **options: Unpack[TG_EditMessageTextOpts],
    ) -> Awaitable[TG_MessageResponse]:
        """
        Edit a text message in a chat

        :param int chat_id: ID of the chat the message to edit is in
        :param int message_id: ID of the message to edit
        :param str text: Text to edit the message to
        :param options: Additional API options
        """
    def edit_message_reply_markup(
        self,
        chat_id: int | str,
        message_id: int,
        reply_markup: str,
        **options: Unpack[TG_EditMessageReplyMarkupOpts],
    ) -> Awaitable[Any]:
        """
        Edit a reply markup of message in a chat

        :param int chat_id: ID of the chat the message to edit is in
        :param int message_id: ID of the message to edit
        :param str reply_markup: New inline keyboard markup for the message
        :param options: Additional API options
        """
    async def get_file(self, file_id: int) -> TG_File:
        """
        Get basic information about a file and prepare it for downloading.

        :param int file_id: File identifier to get information about
        :return: File object (see https://core.telegram.org/bots/api#file)
        """
    def download_file(
        self, file_path: str, range: str | None = None
    ) -> _RequestContextManager:
        """
        Download a file from Telegram servers
        """
    def get_user_profile_photos(
        self, user_id: int, **options: Unpack[TG_GetUserProfilePhotosOpts]
    ) -> Awaitable[Any]:
        """
        Get a list of profile pictures for a user

        :param int user_id: Unique identifier of the target user
        :param options: Additional getUserProfilePhotos options (see
            https://core.telegram.org/bots/api#getuserprofilephotos)
        """
    def stop(self) -> None: ...
    async def webhook_handle(self, request: web.Request) -> web.Response:
        """
        aiohttp.web handle for processing web hooks

        :Example:

        >>> from aiohttp import web
        >>> app = web.Application()
        >>> app.router.add_route('/webhook')
        """
    def create_webhook_app(
        self, path: str, loop: asyncio.AbstractEventLoop | None = None
    ) -> web.Application:
        """
        Shorthand for creating aiohttp.web.Application with registered webhook hanlde
        """
    def set_webhook(
        self, webhook_url: str, **options: Unpack[TG_SetWebhookOpts]
    ) -> Awaitable[Any]:
        """
        Register you webhook url for Telegram service.

        A newly generated UUID will be used as a secret_token parameter
        if it's not specified explicitly
        """
    def delete_webhook(self) -> Awaitable[Any]:
        """
        Tell Telegram to switch back to getUpdates mode
        """
    def on_cleanup(self, action: Callable[[], Any]) -> None:
        """
        You can set an action that will be executed before closing the loop

        :param action: must be a simple callable without any arguments

        :Example:

        >>> bot.on_cleanup(lambda: [t.cancel() for t in tasks])
        """
    @property
    def session(self) -> aiohttp.ClientSession: ...

class InlineQuery:
    """
    Incoming inline query
    See https://core.telegram.org/bots/api#inline-mode for details
    """

    bot: Bot
    sender: Sender
    query_id: str
    query: str
    def __init__(self, bot: Bot, src: TG_InlineQuerySrc) -> None: ...
    def answer(
        self,
        results: list[TG_InlineQueryResult],
        **options: Unpack[TG_InlineQueryAnswerOpts],
    ): ...

class ChosenInlineResult:
    bot: Bot
    sender: Sender
    result_id: str
    location: TG_Location | None
    inline_message_id: str | None
    query: str
    def __init__(self, bot: Bot, src: TG_ChosenInlineResultSrc) -> None: ...

class CallbackQuery:
    bot: Bot
    query_id: str
    data: str
    src: TG_CallbackQuerySrc
    def __init__(self, bot: Bot, src: TG_CallbackQuerySrc) -> None: ...
    def answer(self, **options: Unpack[TG_CallbackQueryOpts]): ...

class PreCheckoutQuery:
    bot: Bot
    sender: Sender
    query_id: str
    currency: str
    total_amount: int
    invoice_payload: str
    def __init__(self, bot: Bot, src: TG_PreCheckoutQuerySrc) -> None: ...
    def answer(self, error_message: str | None = None): ...

class BotApiError(RuntimeError):
    response: ClientResponse
    def __init__(self, *args: object, response: aiohttp.ClientResponse) -> None: ...
