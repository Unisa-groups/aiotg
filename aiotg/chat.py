import logging
from collections.abc import Awaitable
from typing import TYPE_CHECKING, Any, Literal, Unpack, override

from .types_ import (
    TG_BanChatMemberOpts,
    TG_BoolResponse,
    TG_ChatPermissions,
    TG_CopyMessageOpts,
    TG_CopyMessagesOpts,
    TG_CreateChatInviteLinkOpts,
    TG_CreateChatInviteLinkResponse,
    TG_CreateForumTopicOpts,
    TG_CreateForumTopicResponse,
    TG_EditForumTopicOpts,
    TG_EditMessageCaptionOpts,
    TG_EditMessageLiveLocationOpts,
    TG_EditMessageMediaOpts,
    TG_EditMessageTextOpts,
    TG_ForwardMessageOpts,
    TG_GetChatAdministratorResponse,
    TG_GetChatMemberCountResponse,
    TG_GetChatMemberResponse,
    TG_GetChatResponse,
    TG_InlineKeyboardMarkup,
    TG_MaybeInaccessibleMessage,
    TG_MessageResponse,
    TG_PinChatMessageOpts,
    TG_PromoteChatMemberOpts,
    TG_ReactionType,
    TG_ReplyMarkupOpts,
    TG_RestrictChatMemberOpts,
    TG_SendAnimationOpts,
    TG_SendAudioOpts,
    TG_SendContactOpts,
    TG_SendDiceOpts,
    TG_SendDocumentOpts,
    TG_SendFileInput,
    TG_SendLocationOpts,
    TG_SendMediaGroupOpts,
    TG_SendMediaGroupResponse,
    TG_SendMessageOpts,
    TG_SendPhotoOpts,
    TG_SendPollOpts,
    TG_SendStickerOpts,
    TG_SendVenueOpts,
    TG_SendVideoNoteOpts,
    TG_SendVideoOpts,
    TG_SendVoiceOpts,
    TG_SetChatPermissionsOpts,
    TG_StopMessageLiveLocationOpts,
    TG_StringResponse,
    TG_UnpinChatMessageOpts,
)

if TYPE_CHECKING:
    from .bot import Bot

logger = logging.getLogger("aiotg")


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
        return self.bot.send_message(self.id, text, **options)

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
        assert self.message

        opts: TG_SendMessageOpts = {
            "reply_to_message_id": self.message["message_id"],
            "disable_web_page_preview": True,
        }
        if parse_mode is not None:
            opts["parse_mode"] = parse_mode

        if markup is not None:
            opts["reply_markup"] = markup

        return self.send_text(text, **opts)

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
        opts: TG_EditMessageTextOpts = {}
        if markup is not None:
            opts["reply_markup"] = markup
        if parse_mode is not None:
            opts["parse_mode"] = parse_mode

        return self.bot.edit_message_text(self.id, message_id, text, **opts)

    def edit_reply_markup(
        self, message_id: int, markup: TG_ReplyMarkupOpts
    ) -> Awaitable[TG_MessageResponse]:
        """
        Edit only reply markup of the message in this chat.

        :param int message_id: ID of the message to edit
        :param dict markup: Markup options
        """
        return self.bot.edit_message_reply_markup(
            self.id, message_id, reply_markup=self.bot.json_serialize(markup)
        )

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

    def get_chat(self) -> Awaitable[TG_GetChatResponse]:
        """
        Get information about the chat.
        """
        return self.bot.api_call("getChat", chat_id=str(self.id))

    def get_chat_administrators(self) -> Awaitable[TG_GetChatAdministratorResponse]:
        """
        Get a list of administrators in a chat. Chat must not be private.
        """
        return self.bot.api_call("getChatAdministrators", chat_id=str(self.id))

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

    def get_chat_member(self, user_id: int) -> Awaitable[TG_GetChatMemberResponse]:
        """
        Get information about a member of a chat.

        :param int user_id: Unique identifier of the target user
        """
        return self.bot.api_call(
            "getChatMember", chat_id=str(self.id), user_id=str(user_id)
        )

    def send_sticker(
        self, sticker: TG_SendFileInput, **options: Unpack[TG_SendStickerOpts]
    ) -> Awaitable[TG_MessageResponse]:
        """
        Send a sticker to the chat.

        :param sticker: Sticker to send (file or string)
        :param options: Additional sendSticker options (see
            https://core.telegram.org/bots/api#sendsticker)
        """
        return self.bot.api_call(
            "sendSticker", chat_id=str(self.id), sticker=sticker, **options
        )

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
        return self.bot.api_call(
            "sendAudio", chat_id=str(self.id), audio=audio, **options
        )

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
        return self.bot.api_call(
            "sendPhoto", chat_id=str(self.id), photo=photo, caption=caption, **options
        )

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
        return self.bot.api_call(
            "sendVideo", chat_id=str(self.id), video=video, caption=caption, **options
        )

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
        return self.bot.api_call(
            "sendDocument",
            chat_id=str(self.id),
            document=document,
            caption=caption,
            **options,
        )

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
        return self.bot.api_call(
            "sendVoice", chat_id=str(self.id), voice=voice, **options
        )

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
        return self.bot.api_call(
            "sendLocation",
            chat_id=self.id,
            latitude=latitude,
            longitude=longitude,
            **options,
        )

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
        return self.bot.api_call(
            "sendVenue",
            chat_id=self.id,
            latitude=latitude,
            longitude=longitude,
            title=title,
            address=address,
            **options,
        )

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
        return self.bot.api_call(
            "sendContact",
            chat_id=self.id,
            phone_number=phone_number,
            first_name=first_name,
            **options,
        )

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
        return self.bot.api_call("sendChatAction", chat_id=self.id, action=action)

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
        >>>     'type': 'photo',
        >>>     'media': p,
        >>>     'caption': f'{i} of {count}'
        >>> }
        >>> await chat.send_media_group(dumps(tg_album))
        """

        return self.bot.api_call(
            "sendMediaGroup",
            chat_id=str(self.id),
            media=media,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            **options,
        )

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
        options: dict[str, Any] = {"reply_markup": reply_markup} if reply_markup else {}
        return self.bot.api_call(
            "stopPoll", chat_id=self.id, message_id=message_id, **options
        )

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

    def unban_chat_sender_chat(self, sender_chat_id: int) -> Awaitable[TG_BoolResponse]:
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

    def reopen_forum_topic(self, message_thread_id: int) -> Awaitable[TG_BoolResponse]:
        """
        Reopen a closed topic in a forum supergroup.

        :param int message_thread_id: Unique identifier of the target topic
        """
        return self.bot.api_call(
            "reopenForumTopic", chat_id=self.id, message_thread_id=message_thread_id
        )

    def delete_forum_topic(self, message_thread_id: int) -> Awaitable[TG_BoolResponse]:
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
        return self.bot.api_call("editGeneralForumTopic", chat_id=self.id, name=name)

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
        return self.bot.api_call("unpinAllGeneralForumTopicMessages", chat_id=self.id)

    def unban_chat_member(self, user_id: int) -> Awaitable[TG_BoolResponse]:
        """
        Use this method to unban a previously kicked user in a supergroup.
        The bot must be an administrator in the group for this to work.

        :param int user_id: Unique identifier of the target user
        """
        return self.bot.api_call("unbanChatMember", chat_id=self.id, user_id=user_id)

    def delete_message(self, message_id: int) -> Awaitable[TG_BoolResponse]:
        """
        Delete message from this chat

        :param int message_id: ID of the message
        """
        return self.bot.api_call(
            "deleteMessage", chat_id=self.id, message_id=message_id
        )

    def is_group(self) -> bool:
        """
        Check if this chat is a group.

        :return: ``True`` if this chat is a group, ``False`` otherwise
        """
        return self.type == "group" or self.type == "supergroup"

    def __init__(
        self,
        bot: "Bot",
        chat_id: int | str,
        chat_type: Literal["private", "group", "supergroup", "channel"] = "private",
        src_message: TG_MaybeInaccessibleMessage | None = None,
    ):
        self.bot: Bot = bot
        self.message: TG_MaybeInaccessibleMessage | None = src_message
        if src_message and "from" in src_message:
            sender = src_message["from"]
        elif src_message and "sender_chat" in src_message:
            # channel posts, anonymous group admins and linked-channel
            # auto-forwards carry no "from"; "sender_chat" holds the real id
            sender = src_message["sender_chat"]
        else:
            sender = {"first_name": "N/A"}
        self.sender: Sender = Sender(sender)
        self.id: int | str = chat_id
        self.type: Literal["private", "group", "supergroup", "channel"] = chat_type

    @staticmethod
    def from_message(bot: "Bot", message: "TG_MaybeInaccessibleMessage") -> "Chat":
        """
        Create a ``Chat`` object from a message.

        :param Bot bot: ``Bot`` object the message and chat belong to
        :param dict message: Message to base the object on
        :return: A chat object based on the message
        """
        chat = message["chat"]
        return Chat(bot, chat["id"], chat["type"], message)


class Sender(dict[str, Any]):
    """A small wrapper for sender info, mostly used for logging"""

    @override
    def __repr__(self) -> str:
        # "title" for a sender_chat, "first_name" for a user
        name = self.get("first_name") or self.get("title") or "N/A"
        uname = " (%s)" % self["username"] if "username" in self else ""
        return name + uname
