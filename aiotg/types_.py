from typing import Any, Literal, NotRequired, Required, TypedDict

TG_InputFile = Any


class TG_MaskPosition(TypedDict, total=True):
    point: str
    x_shift: float
    y_shift: float
    scale: float


class TG_FileBase(TypedDict, total=True):
    file_id: str
    file_unique_id: str
    file_size: NotRequired[int]


class TG_File(TG_FileBase):
    file_path: NotRequired[str]


class TG_PhotoSize(TG_FileBase, total=True):
    width: int
    height: int


class TG_Animation(TG_PhotoSize, total=False):
    duration: Required[int]
    thumbnail: TG_PhotoSize
    file_name: str
    mime_type: str


class TG_Audio(TG_FileBase, total=False):
    duration: Required[int]
    performer: str
    title: str
    file_name: str
    mime_type: str
    thumbnail: TG_PhotoSize


class TG_Document(TG_FileBase, total=False):
    thumbnail: TG_PhotoSize
    file_name: str
    mime_type: str


class TG_Video(TG_PhotoSize, total=False):
    duration: Required[int]
    thumbnail: TG_PhotoSize
    cover: list[TG_PhotoSize]
    start_timestamp: int
    file_name: str
    mime_type: str


class TG_VideoNote(TG_FileBase, total=False):
    length: Required[int]
    duration: Required[int]
    thumbnail: NotRequired[TG_PhotoSize]


class TG_Sticker(TG_PhotoSize, total=False):
    type: Literal["regular", "mask", "custom_emoji"]
    is_animated: bool
    is_video: bool
    thumbnail: TG_PhotoSize | None
    emoji: str | None
    set_name: str | None
    premium_animation: TG_File | None
    mask_position: TG_MaskPosition
    needs_repainting: bool


# TODO: Add stubs for these, if they're actually used anywhere
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
TG_SuccessfulPayment = Any
TG_RefundedPayment = Any
TG_UsersShared = Any
TG_ChatShared = Any
TG_GiftInfo = Any
TG_UniqueGiftInfo = Any
TG_WriteAccessAllowed = Any
TG_PassportData = Any
TG_ProximityAlertTriggered = Any
TG_ChatBoostAdded = Any
TG_ChatBackground = Any
TG_ChecklistTasksDone = Any
TG_ChecklistTasksAdded = Any
TG_DirectMessagePriceChanged = Any
TG_ForumTopicCreated = Any
TG_ForumTopicEdited = Any
TG_ForumTopicClosed = Any
TG_ForumTopicReopened = Any
TG_GeneralForumTopicHidden = Any
TG_GeneralForumTopicUnhidden = Any
TG_GiveawayCreated = Any
TG_GiveawayCompleted = Any
TG_PaidMessagePriceChanged = Any
TG_VideoChatScheduled = Any
TG_VideoChatStarted = Any
TG_VideoChatEnded = Any
TG_VideoChatParticipantsInvited = Any
TG_WebAppData = Any
TG_WebAppInfo = Any
TG_OrderInfo = Any
TG_LoginUrl = Any
TG_SwitchInlineQueryChosenChat = Any
TG_CopyTextButton = Any
TG_CallbackGame = Any
TG_KeyboardButtonPollType = Any
TG_KeyboardButtonRequestChat = Any
TG_KeyboardButtonRequestUsers = Any
TG_ChatLocation = Any
TG_InlineQueryResult = Any
TG_InlineQueryResultsButton = Any
TG_BusinessConnection = Any
TG_BusinessMessagesDeleted = Any
TG_MessageReactionUpdated = Any
TG_MessageReactionCountUpdated = Any
TG_ShippingQuery = Any
TG_PaidMediaPurchaed = Any
TG_PollAnswer = Any
TG_ChatMemberUpdated = Any
TG_ChatJoinRequest = Any
TG_ChatBoostUpdated = Any
TG_ChatBoostRemoved = Any
TG_InlineQuery = Any
TG_CallbackQuery = Any
TG_PreCheckoutQuery = Any


class TG_ChatPermissions(TypedDict, total=False):
    can_send_messages: bool
    can_send_audios: bool
    can_send_documents: bool
    can_send_photos: bool
    can_send_videos: bool
    can_send_video_notes: bool
    can_send_voice_notes: bool
    can_send_polls: bool
    can_send_other_messages: bool
    can_add_web_page_previews: bool
    can_change_info: bool
    can_invite_users: bool
    can_pin_messages: bool
    can_manage_topics: bool


class TG_AdminPermissions(TypedDict, total=False):
    can_manage_chat: bool
    can_delete_messages: bool
    can_manage_video_chats: bool
    can_restrict_members: bool
    can_promote_members: bool
    can_change_info: bool
    can_invite_users: bool
    can_post_stories: bool
    can_edit_stories: bool
    can_delete_stories: bool
    can_post_messages: bool
    can_edit_messages: bool
    can_pin_messages: bool
    can_manage_topics: bool
    can_manage_direct_messages: bool


class TG_User(TypedDict, total=False):
    id: Required[int]
    is_bot: Required[bool]
    first_name: Required[str]
    last_name: str
    username: str
    language_code: str
    is_premium: bool
    added_to_attachment_menu: bool
    can_join_groups: bool
    can_read_all_group_messages: bool
    supports_inline_queries: bool
    can_connect_to_business: bool
    has_main_web_app: bool


class TG_ChatInviteLink(TypedDict, total=False):
    invite_link: str
    creator: TG_User
    creates_join_request: bool
    is_primary: bool
    is_revoked: bool
    name: str | None
    expire_date: int | None
    member_limit: int | None
    pending_join_request_count: int | None
    subscription_period: int | None
    subscription_price: int | None


TG_Chat = TypedDict(
    "TG_Chat",
    {
        "id": Required[int],
        "type": Required[Literal["private", "group", "supergroup", "channel"]],
        "title": str,
        "username": str,
        "first_name": str,
        "last_name": str,
        "is_forum": bool,
    },
    total=False,
)


class TG_Story(TypedDict, total=True):
    chat: TG_Chat
    id: int


class TG_ChatPhoto(TypedDict, total=False):
    small_file_id: str
    small_file_unique_id: str
    big_file_id: str
    big_file_unique_id: str


class TG_Birthdate(TypedDict, total=True):
    day: int
    month: int
    year: NotRequired[int]


class TG_ForumTopic(TypedDict, total=True):
    message_thread_id: int
    name: str
    icon_color: int
    icon_custom_emoji_id: NotRequired[str]


class TG_ChatFullInfo(TG_Chat):
    accent_color_id: Required[int]
    max_reaction_count: Required[int]
    photo: TG_ChatPhoto
    active_usernames: list[str]
    birthdate: TG_Birthdate
    business_intro: Any
    business_location: Any
    personal_chat: TG_Chat
    available_reactions: list[Any]
    background_custom_emoji_id: str
    profile_accent_color_id: str
    profile_background_custom_emoji_id: str
    emoji_status_expiration_date: int
    bio: str
    has_private_forwards: bool
    has_restricted_voice_and_video_messages: bool
    join_to_send_messages: bool
    join_by_request: bool
    description: str
    invite_link: str
    pinned_message: "TG_Message"
    permissions: Any
    accepted_gift_types: Any
    can_send_paid_media: bool
    slow_mode_delay: int
    unrestrict_boost_count: int
    message_auto_delete_time: int
    has_aggressive_anti_spam_enabled: bool
    has_hidden_members: bool
    has_protected_content: bool
    has_visible_history: bool
    sticker_set_name: str
    can_set_sticker_set: bool
    custom_emoji_sticker_set_name: str
    linked_chat_id: int
    location: TG_ChatLocation


class TG_LinkPreviewOptions(TypedDict, total=False):
    is_disabled: bool
    url: str
    prefer_small_media: bool
    prefer_large_media: bool
    show_above_text: bool


class TG_ReplyParameters(TypedDict, total=False):
    message_id: Required[int]
    chat_id: str | int
    allow_sending_without_reply: bool
    quote: str
    quote_parse_mode: str
    quote_entities: list["TG_MessageEntity"]
    quote_position: int


TG_MessageOriginUser = TypedDict(
    "TG_MessageOriginUser",
    {"type": Literal["user"], "date": int, "sender_user": TG_User},
    total=True,
)
TG_MessageOriginHiddenUser = TypedDict(
    "TG_MessageOriginHiddenUser",
    {"type": Literal["hidden_user"], "date": int, "sender_user_name": str},
    total=True,
)
TG_MessageOriginChat = TypedDict(
    "TG_MessageOriginChat",
    {
        "type": Literal["chat"],
        "date": int,
        "sender_chat": TG_Chat,
        "author_signature": NotRequired[str],
    },
    total=True,
)
TG_MessageOriginChannel = TypedDict(
    "TG_MessageOriginChannel",
    {
        "type": Literal["channel"],
        "date": int,
        "chat": TG_Chat,
        "message_id": int,
        "author_signature": NotRequired[str],
    },
    total=True,
)

TG_MessageOrigin = (
    TG_MessageOriginUser
    | TG_MessageOriginHiddenUser
    | TG_MessageOriginChat
    | TG_MessageOriginChannel
)

TG_MessageEntity = TypedDict(
    "TG_MessageEntity",
    {
        "type": Required[
            Literal[
                "mention",
                "hashtag",
                "cashtag",
                "bot_command",
                "url",
                "email",
                "phone_number",
                "bold",
                "italic",
                "underline",
                "strikethrough",
                "spoiler",
                "blockquote",
                "expandable_blockquote",
                "code",
                "pre",
                "text_link",
                "text_mention",
                "custom_emoji",
            ]
        ],
        "offset": Required[int],
        "length": Required[int],
        "url": str,
        "user": TG_User,
        "language": str,
        "custom_emoji_id": str,
    },
    total=False,
)


class TG_MessageAutoDeleteTimerChanged(TypedDict, total=True):
    message_auto_delete_time: int


class TG_ExternalReplyInfo(TypedDict, total=False):
    origin: Required[TG_MessageOrigin]
    chat: TG_Chat
    message_id: int
    link_preview_options: TG_LinkPreviewOptions
    animation: TG_Animation
    audio: TG_Audio
    document: TG_Document
    paid_media: TG_PaidMedia
    photo: list[TG_PhotoSize]
    sticker: TG_Sticker
    story: TG_Story
    video: TG_Video
    video_note: TG_VideoNote
    voice: TG_Voice
    has_media_spoiler: bool
    checklist: TG_Checklist
    contact: TG_Contact
    dice: TG_Dice
    game: TG_Game
    giveaway: TG_Giveaway
    giveaway_winners: TG_GiveawayWinners
    invoice: TG_Invoice
    location: TG_Location
    poll: TG_Poll
    venue: TG_Venue


TG_Message = TypedDict(
    "TG_Message",
    {
        "message_id": Required[int],
        "message_thread_id": int,
        "from": TG_User,  # (need to convert to other form for this, keyword),
        "sender_chat": TG_Chat,
        "sender_boost_count": int,
        "sender_business_bot": TG_User,
        "date": Required[int],
        "business_connection_id": str,
        "chat": Required[TG_Chat],
        "forward_origin": TG_MessageOrigin,
        "forward_from": TG_User,  # deprecated
        "is_topic_message": bool,
        "is_automatic_forward": bool,
        "reply_to_message": "TG_Message",
        "external_reply": TG_ExternalReplyInfo,
        "quote": TG_TextQuote,
        "reply_to_story": TG_Story,
        "via_bot": TG_User,
        "edit_date": int,
        "has_protected_content": bool,
        "is_from_offline": bool,
        "media_group_id": str,
        "author_signature": str,
        "paid_star_count": int,
        "text": str,
        "entities": list[TG_MessageEntity],
        "link_preview_options": TG_LinkPreviewOptions,
        "effect_id": str,
        "animation": TG_Animation,
        "audio": TG_Audio,
        "document": TG_Document,
        "paid_media": TG_PaidMedia,
        "photo": list[TG_PhotoSize],
        "sticker": TG_Sticker,
        "story": TG_Story,
        "video": TG_Video,
        "video_note": TG_VideoNote,
        "voice": TG_Voice,
        "caption": str,
        "caption_entities": list[TG_MessageEntity],
        "show_caption_above_media": bool,
        "has_media_spoiler": bool,
        "checklist": TG_Checklist,
        "contact": TG_Contact,
        "dice": TG_Dice,
        "game": TG_Game,
        "poll": TG_Poll,
        "venue": TG_Venue,
        "location": TG_Location,
        "new_chat_members": list[TG_User],
        "left_chat_member": TG_User,
        "new_chat_title": str,
        "new_chat_photo": list[TG_PhotoSize],
        "delete_chat_photo": bool,
        "group_chat_created": bool,
        "supergroup_chat_created": bool,
        "channel_chat_created": bool,
        "message_auto_delete_timer_changed": TG_MessageAutoDeleteTimerChanged,
        "migrate_to_chat_id": int,
        "migrate_from_chat_id": int,
        "pinned_message": "TG_MaybeInaccessibleMessage",
        "invoice": TG_Invoice,
        "successful_payment": TG_SuccessfulPayment,
        "refunded_payment": TG_RefundedPayment,
        "users_shared": TG_UsersShared,
        "chat_shared": TG_ChatShared,
        "gift": TG_GiftInfo,
        "unique_gift": TG_UniqueGiftInfo,
        "connected_website": str,
        "write_access_allowed": TG_WriteAccessAllowed,
        "proximity_alert_triggered": TG_ProximityAlertTriggered,
        "boost_added": TG_ChatBoostAdded,
        "chat_background_set": TG_ChatBackground,
        "checklist_tasks_done": TG_ChecklistTasksDone,
        "checklist_tasks_added": TG_ChecklistTasksAdded,
        "direct_message_price_changed": TG_DirectMessagePriceChanged,
        "forum_topic_created": TG_ForumTopicCreated,
        "forum_topic_edited": TG_ForumTopicEdited,
        "forum_topic_closed": TG_ForumTopicClosed,
        "forum_topic_reopened": TG_ForumTopicReopened,
        "general_forum_topic_hidden": TG_GeneralForumTopicHidden,
        "general_forum_topic_unhidden": TG_GeneralForumTopicUnhidden,
        "giveaway_created": TG_GiveawayCreated,
        "giveaway": TG_Giveaway,
        "giveaway_winners": TG_GiveawayWinners,
        "giveaway_completed": TG_GiveawayCompleted,
        "paid_message_price_changed": TG_PaidMessagePriceChanged,
        "video_chat_scheduled": TG_VideoChatScheduled,
        "video_chat_started": TG_VideoChatStarted,
        "video_chat_ended": TG_VideoChatEnded,
        "video_chat_participants_invited": TG_VideoChatParticipantsInvited,
        "web_app_data": TG_WebAppData,
        "reply_markup": "TG_InlineKeyboardMarkup",
        "passport_data": TG_PassportData,
    },
    total=False,
)


class TG_InaccessibleMessage(TypedDict, total=True):
    chat: TG_Chat
    message_id: int
    date: Literal[0]


TG_MaybeInaccessibleMessage = TG_Message | TG_InaccessibleMessage

# ----- CHAT MEMBER TYPES -----

# Not using a base class, because the only common field
# between them is user.
# status is a common field, but always has a specific value
# based on type.


class TG_ChatMemberOwner(TypedDict, total=True):
    status: Literal["creator"]
    user: TG_User
    is_anonymous: bool
    custom_title: NotRequired[str]


class TG_ChatMemberAdministrator(TypedDict, total=True):
    status: Literal["administrator"]
    user: TG_User
    can_be_edited: bool
    is_anonymous: bool
    can_manage_chat: bool
    can_delete_messages: bool
    can_manage_video_chats: bool
    can_restrict_members: bool
    can_promote_members: bool
    can_change_info: bool
    can_invite_users: bool
    can_post_stories: bool
    can_edit_stories: bool
    can_delete_stories: bool
    can_post_messages: NotRequired[bool]
    can_edit_messages: NotRequired[bool]
    can_pin_messages: NotRequired[bool]
    can_manage_topics: NotRequired[bool]
    custom_title: NotRequired[str]


class TG_ChatMemberMember(TypedDict, total=True):
    status: Literal["member"]
    user: TG_User
    until_date: NotRequired[int]


class TG_ChatMemberRestricted(TypedDict, total=True):
    status: Literal["restricted"]
    user: TG_User
    is_member: bool
    can_send_messages: bool
    can_send_audios: bool
    can_add_web_page_previews: bool
    can_change_info: bool
    can_invite_users: bool
    can_pin_messages: bool
    can_manage_topics: bool
    until_date: int


class TG_ChatMemberLeft(TypedDict, total=True):
    status: Literal["left"]
    user: TG_User


class TG_ChatMemberBanned(TypedDict, total=True):
    status: Literal["kicked"]
    user: TG_User
    until_date: int


TG_ChatMember = (
    TG_ChatMemberOwner
    | TG_ChatMemberAdministrator
    | TG_ChatMemberMember
    | TG_ChatMemberRestricted
    | TG_ChatMemberLeft
    | TG_ChatMemberBanned
)

# ---- MARKUP OPTIONS ----


class TG_KeyboardButtonBase(TypedDict, total=False):
    text: Required[str]
    web_app: TG_WebAppInfo


class TG_KeyboardButton(TG_KeyboardButtonBase, total=False):
    request_users: TG_KeyboardButtonRequestUsers
    request_chat: TG_KeyboardButtonRequestChat
    request_contact: bool
    request_location: bool
    request_poll: TG_KeyboardButtonPollType


class TG_InlineKeyboardButton(TG_KeyboardButtonBase, total=False):
    url: str
    callback_data: str
    login_url: TG_LoginUrl
    switch_inline_query: str
    switch_inline_query_current_chat: str
    switch_inline_query_chosen_chat: TG_SwitchInlineQueryChosenChat
    copy_text: TG_CopyTextButton
    callback_game: TG_CallbackGame
    pay: bool


class TG_ReplyKeyboardMarkup(TypedDict, total=False):
    keyboard: Required[list[list[TG_KeyboardButton]]]
    is_persistent: bool
    resize_keyboard: bool
    one_time_keyboard: bool
    input_field_placeholder: str
    selective: bool


class TG_ReplyKeyboardRemove(TypedDict, total=False):
    remove_keyboard: Required[bool]
    selective: bool


class TG_ForceReply(TypedDict, total=False):
    force_reply: Required[bool]
    input_field_placeholder: str
    selective: bool


class TG_InlineKeyboardMarkup(TypedDict, total=True):
    inline_keyboard: list[list[TG_InlineKeyboardButton]]


TG_ReplyMarkupOpts = (
    TG_InlineKeyboardMarkup
    | TG_ReplyKeyboardMarkup
    | TG_ReplyKeyboardRemove
    | TG_ForceReply
)

# ---- SPECIFIC QUERY TYPES ---

TG_PreCheckoutQuerySrc = TypedDict(
    "TG_PreCheckoutQuerySrc",
    {
        "id": str,
        "from": TG_User,
        "currency": str,
        "total_amount": int,
        "invoice_payload": str,
        "shipping_option_id": NotRequired[str],
        "order_info": NotRequired[TG_OrderInfo],
    },
)

TG_CallbackQuerySrc = TypedDict(
    "TG_CallbackQuerySrc",
    {
        "id": str,
        "from": TG_User,
        "message": NotRequired[TG_MaybeInaccessibleMessage],
        "inline_message_id": NotRequired[str],
        "chat_instance": str,
        "data": NotRequired[str],
        "game_short_name": NotRequired[str],
    },
    total=True,
)


class TG_CallbackQueryOpts(TypedDict, total=False):
    text: str
    show_alert: bool
    url: str
    cache_time: int


TG_InlineQuerySrc = TypedDict(
    "TG_InlineQuerySrc",
    {
        "id": str,
        "from": TG_User,
        "query": str,
        "offset": str,
        "chat_type": NotRequired[
            Literal["sender", "private", "group", "supergroup", "channel"]
        ],
        "location": NotRequired[TG_Location],
    },
)


class TG_InlineQueryAnswerOpts(TypedDict, total=False):
    cache_time: int
    is_personal: bool
    next_offset: str
    button: TG_InlineQueryResultsButton


# Options for specific API calls
class TG_GetUserProfilePhotosOpts(TypedDict, total=False):
    offset: int
    limit: int


class TG_SetWebhookOpts(TypedDict, total=False):
    certificate: TG_InputFile
    ip_address: str
    max_connections: int
    allowed_updates: list[str]
    drop_pending_updates: bool
    secret_token: str


class TG_EditMessageReplyMarkupOpts(TypedDict, total=False):
    business_connection_id: str
    inline_message_id: str


class TG_EditMessageCaptionOrTextOpts_API(TypedDict, total=False):
    business_connection_id: str
    chat_id: str | int
    message_id: int
    inline_message_id: str
    parse_mode: str
    link_preview_options: TG_LinkPreviewOptions
    disable_web_page_preview: bool  # deprecated
    reply_markup: TG_InlineKeyboardMarkup
    text: str
    entities: list[TG_MessageEntity]
    caption: str
    caption_entities: list[TG_MessageEntity]


class TG_EditMessageTextOpts(TypedDict, total=False):
    business_connection_id: str
    inline_message_id: str
    parse_mode: str
    entities: list[TG_MessageEntity]
    link_preview_options: TG_LinkPreviewOptions
    disable_web_page_preview: bool  # deprecated
    reply_markup: TG_InlineKeyboardMarkup


class TG_GetChatOpts_API(TypedDict):
    chat_id: str | int


class TG_DeleteMessageOpts_API(TG_GetChatOpts_API):
    chat_id: str | int
    message_id: int


# ---- SENDING OPTIONS ----

TG_SendFileInput = TG_InputFile | str


# Send Media contains all the options that the other ones have
# It is a special case, in that the call already has a
# disable notification field in the function call,
# so it can't be part of opts.
# To get around that, there's a subclass SendOpts,
# that just has that extra field
class TG_SendMediaGroupOpts(TypedDict, total=False):
    business_connection_id: str
    message_thread_id: int
    protect_content: bool
    allow_paid_broadcast: bool
    message_effect_id: str
    reply_parameters: TG_ReplyParameters
    reply_markup: TG_ReplyMarkupOpts


class TG_SendOpts(TG_SendMediaGroupOpts, total=False):
    disable_notification: bool
    disable_web_page_preview: bool  # deprecated
    reply_to_message_id: int


class TG_SendStickerOpts(TG_SendOpts, total=False):
    emoji: str


class TG_SendAudioOpts(TG_SendOpts, total=False):
    caption: str
    parse_mode: str
    caption_entities: list[TG_MessageEntity]
    duration: int
    performer: str
    title: str
    thumbnail: TG_SendFileInput


class TG_SendPhotoOpts(TG_SendOpts, total=False):
    parse_mode: str
    caption_entities: list[TG_MessageEntity]
    show_caption_above_media: bool
    has_spoiler: bool


class TG_SendPhotoOpts_API(TG_SendPhotoOpts, total=False):
    chat_id: Required[str | int]
    photo: Required[TG_SendFileInput]
    caption: str


class TG_SendVideoOpts(TG_SendOpts, total=False):
    duration: int
    width: int
    height: int
    thumbnail: TG_SendFileInput
    cover: TG_SendFileInput
    start_timestamp: int
    parse_mode: str
    caption_entities: list[TG_MessageEntity]
    show_caption_above_media: bool
    has_spoiler: bool
    supports_streaming: bool


class TG_SendDocumentOpts(TG_SendOpts, total=False):
    thumbnail: TG_SendFileInput
    parse_mode: str
    caption_entities: list[TG_MessageEntity]
    disable_content_type_detection: bool


class TG_SendVoiceOpts(TG_SendOpts, total=False):
    caption: str
    parse_mode: str
    caption_entities: list[TG_MessageEntity]
    duration: int


class TG_SendLocationOpts(TG_SendOpts, total=False):
    business_connection_id: str
    horizontal_accuracy: float
    live_period: int
    heading: int
    proximity_alert_radius: int


class TG_SendVenueOpts(TG_SendOpts, total=False):
    foursquare_id: str
    foursquare_type: str
    google_place_id: str
    google_place_type: str


class TG_SendContactOpts(TG_SendOpts, total=False):
    last_name: str
    vcard: str


class TG_SendMessageOpts(TG_SendOpts, total=False):
    parse_mode: Literal["HTML", "Markdown"]
    entities: list[TG_MessageEntity]
    link_preview_options: TG_LinkPreviewOptions
    disable_web_page_preview: bool  # deprecated, but keeping here


class TG_SendMessageOpts_API(TG_SendOpts, total=False):
    text: Required[str]
    chat_id: Required[int]
    parse_mode: Literal["HTML", "Markdown"]


class TG_ForwardMessageOpts(TypedDict, total=False):
    chat_id: Required[str | int]
    message_thread_id: int
    direct_messages_topic_id: int
    from_chat_id: Required[str | int]
    video_start_timestamp: int
    disable_notification: bool
    protect_content: bool
    message_id: Required[int]


class TG_CreateForumTopicOpts(TypedDict, total=False):
    chat_id: Required[str | int]
    name: Required[str]
    icon_color: int
    icon_custom_emoji_id: str


class TG_BanChatMemberOpts(TypedDict, total=False):
    chat_id: Required[str | int]
    user_id: Required[int]
    until_date: int
    revoke_messages: bool


class TG_UnbanChatMemberOpts(TypedDict, total=True):
    chat_id: str | int
    user_id: int
    only_if_banned: NotRequired[bool]


class TG_GetFileOpts(TypedDict, total=True):
    file_id: str


class TG_LeaveChatOpts(TypedDict, total=True):
    chat_id: str | int


class TG_RestrictChatMemberOpts(TypedDict, total=True):
    chat_id: str | int
    user_id: int
    permissions: TG_ChatPermissions
    use_independent_chat_permissions: NotRequired[bool]
    until_date: NotRequired[int]


class TG_PromoteChatMemberOpts(TG_AdminPermissions, total=False):
    chat_id: Required[str | int]
    user_id: Required[int]
    is_anonymous: bool


class TG_CreateChatInviteLinkOpts(TypedDict, total=False):
    chat_id: str | int
    name: NotRequired[str]
    expire_date: NotRequired[int]
    member_limit: NotRequired[int]
    creates_join_request: NotRequired[bool]


class TG_SetChatPermissionsOpts(TypedDict, total=True):
    chat_id: str | int
    permissions: TG_ChatPermissions
    use_independent_chat_permissions: NotRequired[bool]


class TG_GetFileResponse(TypedDict, total=True):
    ok: bool
    result: TG_File


class TG_MessageResponse(TypedDict, total=True):
    ok: bool
    result: TG_Message


class TG_GetChatResponse(TypedDict, total=True):
    ok: bool
    result: TG_ChatFullInfo


class TG_GetChatMemberCountResponse(TypedDict, total=True):
    ok: bool
    result: int


class TG_GetChatMemberResponse(TypedDict, total=True):
    ok: bool
    result: TG_ChatMember


class TG_GetChatAdministratorResponse(TypedDict, total=True):
    ok: bool
    result: list[TG_ChatMember]


class TG_CreateForumTopicResponse(TypedDict, total=True):
    ok: bool
    result: TG_ForumTopic


class TG_BoolResponse(TypedDict, total=True):
    ok: bool
    result: bool


class TG_StringResponse(TypedDict, total=True):
    ok: bool
    result: str


class TG_IntResponse(TypedDict, total=True):
    ok: bool
    result: int


class TG_CreateChatInviteLinkResponse(TypedDict, total=True):
    ok: bool
    result: TG_ChatInviteLink


TG_ChosenInlineResultSrc = TypedDict(
    "TG_ChosenInlineResultSrc",
    {
        "result_id": Required[str],
        "from": Required[TG_User],
        "location": TG_Location,
        "inline_message_id": str,
        "query": Required[str],
    },
    total=False,
)


class TG_UpdateOpts(TypedDict, total=False):
    offset: int
    limit: int
    timeout: int
    allowed_updates: list[str]


class TG_Update(TypedDict, total=False):
    update_id: Required[int]
    message: TG_Message
    edited_message: TG_Message
    channel_post: TG_Message
    edited_channel_post: TG_Message
    business_connection: TG_BusinessConnection
    business_message: TG_Message
    edited_business_message: TG_Message
    deleted_business_messages: TG_BusinessMessagesDeleted
    message_reaction: TG_MessageReactionUpdated
    message_reaction_count: TG_MessageReactionCountUpdated
    inline_query: TG_InlineQuerySrc
    chosen_inline_result: TG_ChosenInlineResultSrc
    callback_query: TG_CallbackQuerySrc
    shipping_query: TG_ShippingQuery
    pre_checkout_query: TG_PreCheckoutQuerySrc
    purchased_paid_media: TG_PaidMediaPurchaed
    poll: TG_Poll
    poll_answer: TG_PollAnswer
    my_chat_member: TG_ChatMemberUpdated
    chat_member: TG_ChatMemberUpdated
    chat_join_request: TG_ChatJoinRequest
    chat_boost: TG_ChatBoostUpdated
    removed_chat_boost: TG_ChatBoostRemoved


class TG_UpdateResponse_Success(TypedDict):
    ok: Literal[True]
    result: list[TG_Update]
    description: NotRequired[str]


class TG_Response_Failure(TypedDict):
    ok: Literal[False]
    description: NotRequired[str]


TG_UpdateResponse = TG_UpdateResponse_Success | TG_Response_Failure


class TG_SendMediaGroupResponse(TypedDict):
    ok: bool
    result: list[TG_Message]
