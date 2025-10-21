import asyncio

from livekit.agents.voice import room_io
from livekit.protocol import sip

from livekit_voice_call_runner.core.call_agent import CallAgent
from livekit_voice_call_runner.core.call_dialer import CallDialer
from livekit_voice_call_runner.core.call_event_listener import CallEventListener
from livekit_voice_call_runner.core.call_room_connector import CallRoomConnector
from livekit_voice_call_runner.core.call_session_starter import CallSessionStarter
from livekit_voice_call_runner.logger import CallLogger
from livekit_voice_call_runner.model import BaseModel


class CallRunnerOutboundConfig(BaseModel):
    phone_number_from: str
    phone_number_to: str
    sip_trunk_id: str
    participant_identity: str
    ringing_timeout: int
    max_call_duration: int


class CallRunnerProps(BaseModel):
    call_agent: CallAgent
    call_room_connector: CallRoomConnector
    call_session_starter: CallSessionStarter
    call_event_listener: CallEventListener
    call_dialer: CallDialer
    outbound_config: CallRunnerOutboundConfig
    logger: CallLogger


class CallRunner:
    def __init__(self, props: CallRunnerProps) -> None:
        self._call_agent = props.call_agent
        self._call_room_connector = props.call_room_connector
        self._call_session_starter = props.call_session_starter
        self._call_event_listener = props.call_event_listener
        self._call_dialer = props.call_dialer
        self._outbound_config = props.outbound_config
        self._logger = props.logger

    async def _run(self):
        await self._call_room_connector.connect()
        await self._call_event_listener.listen_to_room(room=self._call_room_connector.room)
        await self._call_session_starter.start_session(
            call_agent=self._call_agent,
            call_room=self._call_room_connector.room,
            room_input_options=room_io.RoomInputOptions(close_on_disconnect=False),
        )
        await self._call_event_listener.listen_to_session(
            session=self._call_session_starter.session,
            agent=self._call_agent,
        )
        await self._call_dialer.dial(
            request=sip.CreateSIPParticipantRequest(
                room_name=self._call_room_connector.room.name,
                sip_call_to=self._outbound_config.phone_number_to,
                sip_number=self._outbound_config.phone_number_from,
                sip_trunk_id=self._outbound_config.sip_trunk_id,
                participant_identity=self._outbound_config.participant_identity,
                ringing_timeout={"seconds": self._outbound_config.ringing_timeout},
                max_call_duration={"seconds": self._outbound_config.max_call_duration},
                wait_until_answered=True,
            )
        )
        shutdown_event = await asyncio.wait_for(
            self._call_event_listener.wait_for_shutdown(),
            timeout=self._outbound_config.max_call_duration,
        )
        self._logger.info("Call ended.", extra=shutdown_event.model_dump())

    async def _shutdown(self):
        logger_extra = {**self._outbound_config.model_dump()}
        try:
            await self._call_session_starter.shutdown()
            await self._call_room_connector.shutdown()
            await self._call_dialer.shutdown()
            self._logger.info("Successfully shutdown.", extra=logger_extra)
        except Exception:
            self._logger.warning("Failed to shutdown.", exc_info=True, extra=logger_extra)

    async def run(self):
        logger_extra = {**self._outbound_config.model_dump()}
        try:
            self._logger.info("Running.", extra=logger_extra)
            await self._run()
            self._logger.info("Successfully ran.", extra=logger_extra)
        except Exception as e:
            self._logger.error("Failed to run.", extra={**logger_extra, "error": str(e)})
        finally:
            await self._shutdown()
