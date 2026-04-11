from typing import Optional

from livekit import api, protocol

from livekit_voice_call_runner.core.ishutdown import IShutdown
from livekit_voice_call_runner.logger import CallLogger
from livekit_voice_call_runner.model import CallRoom


class CallRoomConnector(IShutdown):
    def __init__(
        self,
        room_name_prefix: str,
        participant_identity: str,
        livekit_url: str,
        livekit_api: api.LiveKitAPI,
        logger: CallLogger,
    ):
        self._room_name_prefix = room_name_prefix
        self._participant_identity = participant_identity
        self._livekit_url = livekit_url
        self._livekit_api = livekit_api
        self._logger = logger
        self._room: Optional[CallRoom] = None

    @property
    def room(self) -> CallRoom:
        if not self._room:
            raise RuntimeError("Room not connected")
        return self._room

    def _get_access_token(self, room_name: str) -> str:
        token = api.AccessToken(
            self._livekit_api.room.api_key,
            self._livekit_api.room.api_secret,
        )
        token.with_identity(
            self._participant_identity,
        ).with_grants(
            api.VideoGrants(room_join=True, room=room_name),
        )
        return token.to_jwt()

    async def _create_room(self) -> CallRoom:
        name = f"{self._room_name_prefix}-{self._logger.correlation_id}"
        await self._livekit_api.room.create_room(protocol.room.CreateRoomRequest(name=name))
        return CallRoom(name=name)

    async def connect(self) -> None:
        logger_extra = {"room_name": self._room_name_prefix}
        self._logger.info("Connecting to room.", extra=logger_extra)

        self._room = await self._create_room()
        await self._room.connect(
            url=self._livekit_url,
            token=self._get_access_token(room_name=self._room.name),
        )

        self._logger.info("Successfully connected to room.", extra=logger_extra)

    async def shutdown(self) -> None:
        logger_extra = {"room_name": self.room.name}
        self._logger.info("Shutting down", extra=logger_extra)

        await self.room.disconnect()
        await self._livekit_api.aclose()

        self._logger.info("Successfully shut down.", extra=logger_extra)
