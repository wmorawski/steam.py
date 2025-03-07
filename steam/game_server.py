"""Licensed under The MIT License (MIT) - Copyright (c) 2020-present James H-B. See LICENSE"""

from __future__ import annotations

from datetime import timedelta
from ipaddress import IPv4Address
from typing import TYPE_CHECKING, Any, Generic, Literal, NamedTuple, TypeAlias, TypeVar

from .app import App, PartialApp
from .enums import Enum, GameServerRegion, Type
from .id import ID
from .protobufs.game_servers import EQueryType, GetServerListResponseServer, QueryResponse

if TYPE_CHECKING:
    from collections.abc import Callable

    from typing_extensions import Unpack

    from .state import ConnectionState

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
Q: TypeAlias = "Query[Q]"

__all__ = (
    "Query",
    "GameServer",
    "ServerPlayer",
)


class Operator(Enum):
    # fmt: off
    div  = "\\"
    nor  = "\\nor\\"
    nand = "\\nand\\"
    # fmt: on

    def format(self, query_1: str, query_2: str) -> str:
        return f"{query_1}{query_2}" if self is Operator.div else f"{self.value}[{query_1}{query_2}]"


class QueryAll:
    def __repr__(self) -> str:
        return self.__class__.__name__

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    query = ""


class QueryMeta(type):
    @property
    def not_empty(cls) -> Q:
        """Fetches servers that are not empty."""
        return Query["Q"](r"\empty\1")

    @property
    def empty(cls) -> Q:
        """Fetches servers that are empty."""
        return Query["Q"](r"\noplayers\1")

    @property
    def proxy(cls) -> Q:
        """Fetches servers that are spectator proxies."""
        return Query["Q"](r"\proxy\1")

    @property
    def whitelisted(cls) -> Q:
        """Fetches servers that are whitelisted."""
        return Query["Q"](r"\white\1")

    @property
    def dedicated(cls) -> Q:
        """Fetches servers that are running dedicated."""
        return Query["Q"](r"\dedicated\1")

    @property
    def secure(cls) -> Q:
        """Fetches servers that are using anti-cheat technology (VAC, but potentially others as well)."""
        return Query["Q"](r"\secure\1")

    @property
    def linux(cls) -> Q:
        """Fetches servers running on a Linux platform."""
        return Query["Q"](r"\linux\1")

    @property
    def no_password(cls) -> Q:
        """Fetches servers that are not password protected."""
        return Query["Q"](r"\password\0")

    @property
    def not_full(cls) -> Q:
        """Fetches servers that are not full."""
        return Query["Q"](r"\full\1")

    @property
    def unique_addresses(cls) -> Q:
        """Fetches only one server for each unique IP address matched."""
        return Query["Q"]("\\collapse_addr_hash\\1")

    @property
    def version_match(cls) -> Query[str]:
        """Fetches servers running version "x" (``"*"`` is wildcard)."""
        return Query["str"]("\\version_match\\", type=str)

    @property
    def name_match(cls) -> Query[str]:
        """Fetches servers with their hostname matching "x" (``"*"`` is wildcard)."""
        return Query["str"]("\\name_match\\", type=str)

    @property
    def running_mod(cls) -> Query[str]:
        """Fetches servers running the specified modification (e.g. cstrike)."""
        return Query["str"]("\\gamedir\\", type=str)

    @property
    def running_map(cls) -> Query[str]:
        """Fetches servers running the specified map (e.g. cs_italy)"""
        return Query["str"]("\\map\\", type=str)

    @property
    def ip(cls) -> Query[str]:
        """Fetches servers on the specified IP address, port is optional.

        See Also
        --------
        :meth:`Client.fetch_server` for a Query free version of this.
        """
        return Query["str"]("\\gameaddr\\", type=str)

    @property
    def running(cls) -> Query[App | int]:
        """Fetches servers running a :class:`.App` or an :class:`int` app id."""
        return Query["App | int"]("\\appid\\", type=(App, int), callback=lambda app: getattr(app, "id", app))

    @property
    def not_running(cls) -> Query[App | int]:
        """Fetches servers not running a :class:`.App` or an :class:`int` app id."""
        return Query["App | int"]("\\nappid\\", type=(App, int), callback=lambda app: getattr(app, "id", app))

    @property
    def match_tags(cls) -> Query[list[str]]:
        """Fetches servers with all the given tag(s) in :attr:`GameServer.tags`."""
        return Query["list[str]"]("\\gametype\\", type=list, callback=lambda items: f"[{','.join(items)}]")

    @property
    def match_hidden_tags(cls) -> Query[list[str]]:
        """Fetches servers with all the given tag(s) in their 'hidden' tags only applies for :attr:`steam.LFD2`."""
        return Query["list[str]"]("\\gamedata\\", type=list, callback=lambda items: f"[{','.join(items)}]")

    @property
    def match_any_hidden_tags(cls) -> Query[list[str]]:
        """Fetches servers with any of the given tag(s) in their 'hidden' tags only applies for :attr:`steam.LFD2`."""
        return Query["list[str]"]("\\gamedataor\\", type=list, callback=lambda items: f"[{','.join(items)}]")

    @property
    def region(cls) -> Query[GameServerRegion]:
        """Fetches servers in a given region."""
        return Query["GameServerRegion"]("\\region\\", type=GameServerRegion, callback=lambda region: region.value)

    @property
    def all(cls) -> QueryAll:
        """Fetches any servers. Any operations on this will fail."""
        return QueryAll()


class Query(Generic[T_co], metaclass=QueryMeta):
    r"""A :class:`pathlib.Path` like class for constructing Global Master Server queries.

    .. container:: operations

        .. describe:: x == y

            Checks if two queries are equal, order is checked.

        .. describe:: x / y

            Appends y's query to x.

        .. describe:: x | y

            Combines the two queries in ``\nor\[x\y]`` (not or).

        .. describe:: x & y

            Combines the two queries in ``\nand\[x\y]`` (not and).

    Examples
    --------

    Match servers running TF2, that are not empty and are using VAC

    .. code-block:: pycon

        >>> Query.running / TF2 / Query.not_empty / Query.secure
        <Query query='\\appid\\440\\empty\\1\\secure\\1'>


    Matches servers that are not empty, not full and are not using VAC

    .. code-block:: pycon

        >>> Query.not_empty / Query.not_full | Query.secure
        <Query query='\\empty\\1\\nor\\[\\full\\1\\secure\\1]'>

    Match servers where the server name is not "A cool Server" or the server doesn't support alltalk or increased max
    players

    .. code-block:: pycon

        >>> Query.name_match / "A not cool server" | Query.match_tags / ["alltalk", "increased_maxplayers"]
        <Query query='\\nor\\[\\name_match\\A not cool server\\gametype\\[alltalk,increased_maxplayers]]'>

    Match servers where the server is not on linux and the server doesn't have no password (has a password)

    .. code-block:: pycon

        >>> Query.linux & Query.no_password
    """

    # simple specification:
    # - immutable
    # - based on https://developer.valvesoftware.com/wiki/Master_Server_Query_Protocol

    # TODO use __invert__ to do some cool manipulation where possible and generally change the dunders cause they make
    # little sense atm
    __slots__ = ("_raw", "_type", "_callback")
    _raw: tuple[Query[Any], Operator, T_co] | tuple[str]
    _type: type[T_co] | tuple[type[T_co], ...] | None
    _callback: Callable[[T_co], Any] | None

    def __new__(
        cls,
        *raw: Unpack[tuple[Query[Any], Operator, T_co]] | Unpack[tuple[str]],
        type: type[T_co] | tuple[type[T_co], ...] | None = None,
        callback: Callable[[T_co], Any] = lambda x: x,
    ) -> Query[T_co]:
        self = super().__new__(cls)
        self._raw = raw  # type: ignore  # can't tell if this is a pyright bug
        self._type = type
        self._callback = callback
        return self

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} query={self.query!r}>"

    # it's safe to use a covariant TypeVar here as everything is read-only
    def _process_op(self, other: T_co, op: Operator) -> Q:  # type: ignore
        cls = self.__class__

        if self._type is not None and isinstance(other, self._type):
            return cls(self, op, other)

        if not isinstance(other, Query):
            return NotImplemented

        return cls(self, op, other, type=other._type, callback=other._callback)

    def __truediv__(self, other: T_co) -> Q:  # type: ignore
        return self._process_op(other, Operator.div)

    def __and__(self, other: T_co) -> Q:  # type: ignore
        return self._process_op(other, Operator.nand)

    def __or__(self, other: T_co) -> Q:  # type: ignore
        return self._process_op(other, Operator.nor)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Query) and self._raw == other._raw

    @property
    def query(self) -> str:
        """The actual query used for querying Global Master Servers."""

        if len(self._raw) == 1:  # string query
            return self._raw[0]

        # normal
        query_1, op, query_2 = self._raw

        return op.format(
            query_1.query,
            query_2.query if isinstance(query_2, Query) else query_1._callback(query_2),
        )


class ServerPlayer(NamedTuple):
    name: str
    score: int
    play_time: timedelta


class GameServer(ID[Literal[Type.GameServer]]):
    """Represents a game server."""

    __slots__ = (
        "name",
        "app",
        "ip",
        "port",
        "tags",
        "map",
        "bot_count",
        "player_count",
        "max_player_count",
        "region",
        "version",
        "_secure",
        "_dedicated",
        "_state",
    )

    def __init__(self, state: ConnectionState, server: GetServerListResponseServer):
        super().__init__(server.steamid, type=Type.GameServer)
        self.name = server.name
        """The name of the server."""
        self.app = PartialApp(state, id=server.appid)
        """The app of the server."""
        self.ip = IPv4Address(server.addr.rpartition(":")[0])
        """The ip of the server."""
        self.port = server.gameport
        """The port of the server."""
        self.tags = server.gametype.split(",")
        """The tags of the server."""
        self.map = server.map
        """The map the server is running."""
        self.bot_count = server.bots
        """The number of bots in the server."""
        self.player_count = server.players
        """The number of players the server."""
        self.max_player_count = server.max_players
        """The maximum player count of the server."""
        self.region = GameServerRegion.try_value(server.region)
        """The region the server is in."""
        self.version = server.version
        """The version of the server."""

        self._secure = server.secure
        self._dedicated = server.dedicated
        self._state = state

    def __repr__(self) -> str:
        attrs = ("name", "app", "ip", "port", "region", "id", "universe", "instance")
        resolved = [f"{attr}={getattr(self, attr)!r}" for attr in attrs]
        return f"<{self.__class__.__name__} {' '.join(resolved)}>"

    def __str__(self) -> str:
        return self.name

    def is_secure(self) -> bool:
        """Whether the sever is secured, likely with VAC."""
        return self._secure

    def is_dedicated(self) -> bool:
        """Whether the sever is dedicated."""
        return self._dedicated

    async def _query(self, type: EQueryType) -> QueryResponse:
        return await self._state.query_server(int(self.ip), self.port, self.app.id, type)

    # async def ping(self):  # FIXME not sure how to expose this
    #     proto = await self._query(EQueryType.Ping)
    #     proto.ping_data

    async def players(self) -> list[ServerPlayer]:
        """Fetch a server's players.

        Returns
        -------
        .. source:: steam.ServerPlayer
        """
        proto = await self._query(EQueryType.Players)
        return [
            ServerPlayer(
                name=player.name,
                score=player.score,
                play_time=timedelta(seconds=player.time_played),
            )
            for player in proto.players_data.players
        ]

    async def rules(self) -> dict[str, str]:
        """Fetch a console variables. e.g. ``sv_gravity`` or ``sv_voiceenable``."""
        proto = await self._query(EQueryType.Rules)
        return proto.rules_data.rules
