import logging
from .bot import Bot as Bot
from .types_ import (
    TG_BoolResponse as TG_BoolResponse,
    TG_EditMessageTextOpts as TG_EditMessageTextOpts,
    TG_GetChatAdministratorResponse as TG_GetChatAdministratorResponse,
    TG_GetChatMemberCountResponse as TG_GetChatMemberCountResponse,
    TG_GetChatMemberResponse as TG_GetChatMemberResponse,
    TG_GetChatResponse as TG_GetChatResponse,
    TG_InlineKeyboardMarkup as TG_InlineKeyboardMarkup,
    TG_MaybeInaccessibleMessage as TG_MaybeInaccessibleMessage,
    TG_MessageResponse as TG_MessageResponse,
    TG_ReplyMarkupOpts as TG_ReplyMarkupOpts,
    TG_SendAudioOpts as TG_SendAudioOpts,
    TG_SendContactOpts as TG_SendContactOpts,
    TG_SendDocumentOpts as TG_SendDocumentOpts,
    TG_SendFileInput as TG_SendFileInput,
    TG_SendLocationOpts as TG_SendLocationOpts,
    TG_SendMediaGroupOpts as TG_SendMediaGroupOpts,
    TG_SendMediaGroupResponse as TG_SendMediaGroupResponse,
    TG_SendMessageOpts as TG_SendMessageOpts,
    TG_SendPhotoOpts as TG_SendPhotoOpts,
    TG_SendStickerOpts as TG_SendStickerOpts,
    TG_SendVenueOpts as TG_SendVenueOpts,
    TG_SendVideoOpts as TG_SendVideoOpts,
    TG_SendVoiceOpts as TG_SendVoiceOpts,
)
from collections.abc import Awaitable
from typing import Any, Literal, Unpack

logger: logging.Logger

class Chat:
    """
    Wrapper for telegram chats, passed to most callbacks
    """
    def send_text(
        self, text: str, **options: Unpack[TG_SendMessageOpts]
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send a text message to the chat.

        :param str text: Text of the message to send
        :param options: Additional sendMessage options (see
            https://core.telegram.org/bots/api#sendmessage
        """
    def reply(
        self,
        text: str,
        markup: TG_ReplyMarkupOpts | None = None,
        parse_mode: Literal["Markdown", "HTML"] | None = None,
    ) -> Awaitable[TG_MessageResponse]:
        """
        Reply to the message this `Chat` object is based on.

        :param str text: Text of the message to send
        :param dict markup: Markup options
        :param str parse_mode: Text parsing mode (``"Markdown"``, ``"HTML"`` or
            ``None``)
        """
    def edit_text(
        self,
        message_id: int,
        text: str,
        markup: TG_InlineKeyboardMarkup | None = None,
        parse_mode: Literal["Markdown", "HTML"] | None = None,
    ) -> Awaitable[TG_MessageResponse]:
        """
        Edit the message in this chat.

        :param int message_id: ID of the message to edit
        :param str text: Text to edit the message to
        :param dict markup: Markup options
        :param str parse_mode: Text parsing mode (``"Markdown"``, ``"HTML"`` or
            ``None``)
        """
    def edit_reply_markup(
        self, message_id: int, markup: TG_ReplyMarkupOpts
    ) -> Awaitable[TG_MessageResponse]:
        """
        Edit only reply markup of the message in this chat.

        :param int message_id: ID of the message to edit
        :param dict markup: Markup options
        """
    def get_chat(self) -> Awaitable[TG_GetChatResponse]:
        """
        Get information about the chat.
        """
    def get_chat_administrators(self) -> Awaitable[TG_GetChatAdministratorResponse]:
        """
        Get a list of administrators in a chat. Chat must not be private.
        """
    def get_chat_members_count(self) -> Awaitable[TG_GetChatMemberCountResponse]:
        """
        Get the number of members in a chat.
        """
    def get_chat_member(self, user_id: int) -> Awaitable[TG_GetChatMemberResponse]:
        """
        Get information about a member of a chat.

        :param int user_id: Unique identifier of the target user
        """
    def send_sticker(
        self, sticker: TG_SendFileInput, **options: Unpack[TG_SendStickerOpts]
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send a sticker to the chat.

        :param sticker: Sticker to send (file or string)
        :param options: Additional sendSticker options (see
            https://core.telegram.org/bots/api#sendsticker)
        """
    def send_audio(
        self, audio: TG_SendFileInput, **options: Unpack[TG_SendAudioOpts]
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send an mp3 audio file to the chat.

        :param audio: Object containing the audio data
        :param options: Additional sendAudio options (see
            https://core.telegram.org/bots/api#sendaudio)

        :Example:

        >>> with open("foo.mp3", "rb") as f:
        >>>     await chat.send_audio(f, performer="Foo", title="Eversong")
        """
    def send_photo(
        self,
        photo: TG_SendFileInput,
        caption: str = "",
        **options: Unpack[TG_SendPhotoOpts],
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send a photo to the chat.

        :param photo: Object containing the photo data
        :param str caption: Photo caption (optional)
        :param options: Additional sendPhoto options (see
            https://core.telegram.org/bots/api#sendphoto)

        :Example:

        >>> with open("foo.png", "rb") as f:
        >>>     await chat.send_photo(f, caption="Would you look at this!")
        """
    def send_video(
        self,
        video: TG_SendFileInput,
        caption: str = "",
        **options: Unpack[TG_SendVideoOpts],
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send an mp4 video file to the chat.

        :param video: Object containing the video data
        :param str caption: Video caption (optional)
        :param options: Additional sendVideo options (see
            https://core.telegram.org/bots/api#sendvideo)

        :Example:

        >>> with open("foo.mp4", "rb") as f:
        >>>     await chat.send_video(f)
        """
    def send_document(
        self,
        document: TG_SendFileInput,
        caption: str = "",
        **options: Unpack[TG_SendDocumentOpts],
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send a general file.

        :param document: Object containing the document data
        :param str caption: Document caption (optional)
        :param options: Additional sendDocument options (see
            https://core.telegram.org/bots/api#senddocument)

        :Example:

        >>> with open("file.doc", "rb") as f:
        >>>     await chat.send_document(f)
        """
    def send_voice(
        self, voice: TG_SendFileInput, **options: Unpack[TG_SendVoiceOpts]
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send an OPUS-encoded .ogg audio file.

        :param voice: Object containing the audio data
        :param options: Additional sendVoice options (see
            https://core.telegram.org/bots/api#sendvoice)

        :Example:

        >>> with open("voice.ogg", "rb") as f:
        >>>     await chat.send_voice(f)
        """
    def send_location(
        self, latitude: float, longitude: float, **options: Unpack[TG_SendLocationOpts]
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send a point on the map.

        :param float latitude: Latitude of the location
        :param float longitude: Longitude of the location
        :param options: Additional sendLocation options (see
            https://core.telegram.org/bots/api#sendlocation)
        """
    def send_venue(
        self,
        latitude: float,
        longitude: float,
        title: str | bytes,
        address: str | bytes,
        **options: Unpack[TG_SendVenueOpts],
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send information about a venue.

        :param float latitude: Latitude of the location
        :param float longitude: Longitude of the location
        :param str title: Name of the venue
        :param str address: Address of the venue
        :param options: Additional sendVenue options (see
            https://core.telegram.org/bots/api#sendvenue)
        """
    def send_contact(
        self,
        phone_number: str,
        first_name: str | bytes,
        **options: Unpack[TG_SendContactOpts],
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send phone contacts.

        :param str phone_number: Contact's phone number
        :param str first_name: Contact's first name
        :param options: Additional sendContact options (see
            https://core.telegram.org/bots/api#sendcontact)
        """
    def send_chat_action(
        self,
        action: Literal[
            "typing",
            "upload_photo",
            "record_video",
            "upload_video",
            "record_audio",
            "upload_audio",
            "upload_document",
            "find_location",
        ],
    ) -> Awaitable[TG_BoolResponse]:
        """
        Send a chat action, to tell the user that something is happening on the
        bot's side.

        Available actions:

        *  `typing` for text messages
        *  `upload_photo` for photos
        *  `record_video` and `upload_video` for videos
        *  `record_audio` and `upload_audio` for audio files
        *  `upload_document` for general files
        *  `find_location` for location data

        :param str action: Type of action to broadcast
        """
    def send_media_group(
        self,
        media: str,
        disable_notification: bool = False,
        reply_to_message_id: int | None = None,
        **options: Unpack[TG_SendMediaGroupOpts],
    ) -> Awaitable[TG_SendMediaGroupResponse]:
        """
        Send a group of photos or videos as an album

        :param media: A JSON-serialized array describing photos and videos
        to be sent, must include 2–10 items
        :param disable_notification: Sends the messages silently. Users will
        receive a notification with no sound.
        :param reply_to_message_id: If the messages are a reply, ID of the original message
        :param options: Additional sendMediaGroup options (see
        https://core.telegram.org/bots/api#sendmediagroup)

        :Example:
        >>> from json import dumps
        >>> photos_urls = [
        >>>     "https://telegram.org/img/t_logo.png",
        >>>     "https://telegram.org/img/SiteAndroid.jpg?1",
        >>>     "https://telegram.org/img/SiteiOs.jpg?1",
        >>>     "https://telegram.org/img/SiteWP.jpg?2"
        >>> ]
        >>> tg_album = []
        >>> count = len(photos_urls)
        >>> for i, p in enumerate(photos_urls):
        >>> {
        >>>     \'type\': \'photo\',
        >>>     \'media\': p,
        >>>     \'caption\': f\'{i} of {count}\'
        >>> }
        >>> await chat.send_media_group(dumps(tg_album))
        """
    def forward_message(
        self, from_chat_id: int, message_id: int
    ) -> Awaitable[TG_MessageResponse]:
        """
        Forward a message from another chat to this chat.

        :param int from_chat_id: ID of the chat to forward the message from
        :param int message_id: ID of the message to forward
        """
    def kick_chat_member(self, user_id: int) -> Awaitable[TG_BoolResponse]:
        """
        Use this method to kick a user from a group or a supergroup.
        The bot must be an administrator in the group for this to work.

        :param int user_id: Unique identifier of the target user
        """
    def unban_chat_member(self, user_id: int) -> Awaitable[TG_BoolResponse]:
        """
        Use this method to unban a previously kicked user in a supergroup.
        The bot must be an administrator in the group for this to work.

        :param int user_id: Unique identifier of the target user
        """
    def delete_message(self, message_id: int) -> Awaitable[TG_BoolResponse]:
        """
        Delete message from this chat

        :param int message_id: ID of the message
        """
    def is_group(self) -> bool:
        """
        Check if this chat is a group.

        :return: ``True`` if this chat is a group, ``False`` otherwise
        """
    bot: Bot
    message: TG_MaybeInaccessibleMessage | None
    sender: Sender
    id: int | str
    type: Literal["private", "group", "supergroup", "channel"]
    def __init__(
        self,
        bot: Bot,
        chat_id: int | str,
        chat_type: Literal["private", "group", "supergroup", "channel"] = "private",
        src_message: TG_MaybeInaccessibleMessage | None = None,
    ) -> None: ...
    @staticmethod
    def from_message(bot: Bot, message: TG_MaybeInaccessibleMessage) -> Chat:
        """
        Create a ``Chat`` object from a message.

        :param Bot bot: ``Bot`` object the message and chat belong to
        :param dict message: Message to base the object on
        :return: A chat object based on the message
        """

class Sender(dict[str, Any]):
    """A small wrapper for sender info, mostly used for logging"""
