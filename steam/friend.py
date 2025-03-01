"""Licensed under The MIT License (MIT) - Copyright (c) 2020-present James H-B. See LICENSE"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Literal

from .profile import FriendProfile
from .user import ClientUser, WrapsUser

if TYPE_CHECKING:
    from .app import App
    from .clan import Clan
    from .enums import Language
    from .group import Group

__all__ = ("Friend",)


class Friend(WrapsUser):
    """Represents a friend of the :class:`ClientUser`."""

    __slots__ = ()

    profile_info = ClientUser.profile_info

    async def profile(self, *, language: Language | None = None) -> FriendProfile:
        return FriendProfile(
            *await asyncio.gather(
                self.equipped_profile_items(language=language),
                self.profile_info(),
                self.profile_customisation_info(),
            )
        )

    async def owns(self, app: App) -> bool:
        """Whether the app is owned by this friend.

        Parameters
        ----------
        app
            The app you want to check the ownership of.
        """
        return self.id64 in await self._state.fetch_friends_who_own(app.id)

    async def invite_to_group(self, group: Group) -> None:
        """Invites the user to a :class:`Group`.

        Parameters
        -----------
        group
            The group to invite the user to.
        """
        await self._state.invite_user_to_chat_group(self.id64, group.id)

    async def invite_to_clan(self, clan: Clan) -> None:
        """Invites the user to a :class:`Clan`.

        Parameters
        -----------
        clan
            The clan to invite the user to.
        """
        await self._state.http.invite_user_to_clan(self.id64, clan.id64)

    # TODO, probably needs client.friends_activity or something
    # async def posts(self):
    #     ...

    if TYPE_CHECKING:

        def is_friend(self) -> Literal[True]:
            ...
