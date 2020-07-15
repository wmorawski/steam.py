# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: steammessages_gamenotifications.proto
# plugin: python-betterproto

from dataclasses import dataclass
from typing import List

import betterproto


@dataclass
class CGameNotificationsVariable(betterproto.Message):
    key: str = betterproto.string_field(1)
    value: str = betterproto.string_field(2)


@dataclass
class CGameNotificationsLocalizedText(betterproto.Message):
    token: str = betterproto.string_field(1)
    variables: List["CGameNotificationsVariable"] = betterproto.message_field(2)
    rendered_text: str = betterproto.string_field(3)


@dataclass
class CGameNotificationsUserStatus(betterproto.Message):
    steamid: int = betterproto.fixed64_field(1)
    state: str = betterproto.string_field(2)
    title: "CGameNotificationsLocalizedText" = betterproto.message_field(3)
    message: "CGameNotificationsLocalizedText" = betterproto.message_field(4)


@dataclass
class CGameNotificationsCreateSessionRequest(betterproto.Message):
    appid: int = betterproto.uint32_field(1)
    context: int = betterproto.uint64_field(2)
    title: "CGameNotificationsLocalizedText" = betterproto.message_field(3)
    users: List["CGameNotificationsUserStatus"] = betterproto.message_field(4)
    steamid: int = betterproto.fixed64_field(5)


@dataclass
class CGameNotificationsCreateSessionResponse(betterproto.Message):
    sessionid: int = betterproto.uint64_field(1)


@dataclass
class CGameNotificationsDeleteSessionRequest(betterproto.Message):
    sessionid: int = betterproto.uint64_field(1)
    appid: int = betterproto.uint32_field(2)
    steamid: int = betterproto.fixed64_field(3)


@dataclass
class CGameNotificationsDeleteSessionResponse(betterproto.Message):
    pass


@dataclass
class CGameNotificationsUpdateSessionRequest(betterproto.Message):
    sessionid: int = betterproto.uint64_field(1)
    appid: int = betterproto.uint32_field(2)
    title: "CGameNotificationsLocalizedText" = betterproto.message_field(3)
    users: List["CGameNotificationsUserStatus"] = betterproto.message_field(4)
    steamid: int = betterproto.fixed64_field(6)


@dataclass
class CGameNotificationsUpdateSessionResponse(betterproto.Message):
    pass


@dataclass
class CGameNotificationsEnumerateSessionsRequest(betterproto.Message):
    appid: int = betterproto.uint32_field(1)
    include_all_user_messages: bool = betterproto.bool_field(3)
    include_auth_user_message: bool = betterproto.bool_field(4)
    language: str = betterproto.string_field(5)


@dataclass
class CGameNotificationsSession(betterproto.Message):
    sessionid: int = betterproto.uint64_field(1)
    appid: int = betterproto.uint64_field(2)
    context: int = betterproto.uint64_field(3)
    title: "CGameNotificationsLocalizedText" = betterproto.message_field(4)
    time_created: int = betterproto.uint32_field(5)
    time_updated: int = betterproto.uint32_field(6)
    user_status: List["CGameNotificationsUserStatus"] = betterproto.message_field(7)


@dataclass
class CGameNotificationsEnumerateSessionsResponse(betterproto.Message):
    sessions: List["CGameNotificationsSession"] = betterproto.message_field(1)


@dataclass
class CGameNotificationsGetSessionDetailsRequest(betterproto.Message):
    sessions: List["CGameNotificationsGetSessionDetailsRequestRequestedSession"] = betterproto.message_field(1)
    appid: int = betterproto.uint32_field(2)
    language: str = betterproto.string_field(3)


@dataclass
class CGameNotificationsGetSessionDetailsRequestRequestedSession(betterproto.Message):
    sessionid: int = betterproto.uint64_field(1)
    include_auth_user_message: bool = betterproto.bool_field(3)


@dataclass
class CGameNotificationsGetSessionDetailsResponse(betterproto.Message):
    sessions: List["CGameNotificationsSession"] = betterproto.message_field(1)


@dataclass
class GameNotificationSettings(betterproto.Message):
    appid: int = betterproto.uint32_field(1)
    allow_notifications: bool = betterproto.bool_field(2)


@dataclass
class CGameNotificationsUpdateNotificationSettingsRequest(betterproto.Message):
    game_notification_settings: List["GameNotificationSettings"] = betterproto.message_field(1)


@dataclass
class CGameNotificationsUpdateNotificationSettingsResponse(betterproto.Message):
    pass


@dataclass
class CGameNotificationsOnNotificationsRequestedNotification(betterproto.Message):
    steamid: int = betterproto.fixed64_field(1)
    appid: int = betterproto.uint32_field(2)


@dataclass
class CGameNotificationsOnUserStatusChangedNotification(betterproto.Message):
    steamid: int = betterproto.fixed64_field(1)
    sessionid: int = betterproto.uint64_field(2)
    appid: int = betterproto.uint32_field(3)
    status: "CGameNotificationsUserStatus" = betterproto.message_field(4)
    removed: bool = betterproto.bool_field(5)
