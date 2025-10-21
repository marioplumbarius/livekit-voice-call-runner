import asyncio
from typing import Any, Optional

from livekit import rtc
from livekit.agents import AgentSession, ChatMessage, ConversationItemAddedEvent, ErrorEvent
from openai import BaseModel

from livekit_voice_call_runner.core.call_agent import CallAgent
from livekit_voice_call_runner.livekit import disconnect_reason_mapper
from livekit_voice_call_runner.logger import CallLogger
from livekit_voice_call_runner.model import CallRoom


class ShutdownEvent(BaseModel):
    reason: str
    context: dict[str, Any]


class CallEventListener:
    def __init__(self, logger: CallLogger):
        self._logger = logger
        self._shutdown_event: Optional[ShutdownEvent] = None

    async def wait_for_shutdown(self) -> ShutdownEvent:
        while not self._shutdown_event:
            await asyncio.sleep(5.0)
        return self._shutdown_event

    async def listen_to_room(self, room: CallRoom) -> None:
        self._logger.info("Listening to room.", extra={"room_name": room.name})

        @room.on("participant_connected")
        def _on_participant_connected(participant: rtc.RemoteParticipant):
            self._logger.info(
                "Participant connected.",
                extra={"participant_identity": participant.identity},
            )

        @room.on("participant_disconnected")
        def _on_participant_disconnected(participant: rtc.RemoteParticipant):
            context = {"participant_identity": participant.identity}
            reason = "Participant disconnected"
            if not self._shutdown_event:
                self._shutdown_event = ShutdownEvent(reason=reason, context=context)

            self._logger.info(reason, extra=context)

        # TODO: check if this is needed at all
        @room.on("track_published")
        def _on_track_published(publication: rtc.RemoteTrackPublication):
            if publication.kind == rtc.TrackKind.KIND_AUDIO:
                publication.set_subscribed(True)
                self._logger.info(
                    "Subscribed to track.",
                    extra={"publication_name": publication.name},
                )

        @room.on("disconnected")
        def _on_disconnected(disconnect_reason: rtc.DisconnectReason):
            context = {"reason": disconnect_reason_mapper.map_to_name(reason=disconnect_reason)}
            reason = "Call agent lost connection"
            if not self._shutdown_event:
                self._shutdown_event = ShutdownEvent(reason=reason, context=context)

            self._logger.info(reason, extra=context)

    async def listen_to_session(self, session: AgentSession, agent: CallAgent):
        self._logger.info("Listening to session.")

        @session.on("conversation_item_added")
        def _on_conversation_item_added(event: ConversationItemAddedEvent):
            if isinstance(event.item, ChatMessage):
                self._logger.info(f"[{event.item.role}] {event.item.text_content}")
                asyncio.create_task(agent.on_chat_message_added(event.item))

        @session.on("error")
        def _on_error(event: ErrorEvent):
            context = event.model_dump()
            reason = "Unexpected error in session"
            if not self._shutdown_event:
                self._shutdown_event = ShutdownEvent(reason=reason, context=context)

            self._logger.error(reason, extra=context)
