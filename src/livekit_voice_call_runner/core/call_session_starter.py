import asyncio
import time
from typing import Optional

from livekit.agents import NOT_GIVEN, AgentSession, NotGivenOr
from livekit.agents.voice import room_io

from livekit_voice_call_runner.core.call_agent import CallAgent
from livekit_voice_call_runner.logger import CallLogger
from livekit_voice_call_runner.model import CallRoom, CallSessionStarterConfigRealtime

_READY_AGENT_STATES = ["idle", "listening", "thinking", "speaking"]


class CallSessionStarter:
    def __init__(
        self,
        config: CallSessionStarterConfigRealtime,
        agent_ready_timeout_seconds: float,
        logger: CallLogger,
    ):
        self._config = config
        self._agent_ready_timeout_seconds = agent_ready_timeout_seconds
        self._logger = logger
        self._session: Optional[AgentSession] = None

    @property
    def session(self) -> AgentSession:
        if not self._session:
            raise RuntimeError("Session not started")
        return self._session

    def _create_session(self) -> AgentSession:
        return AgentSession(
            llm=self._config.llm,
            user_away_timeout=self._config.user_away_timeout,
            use_tts_aligned_transcript=self._config.use_tts_aligned_transcript,
            preemptive_generation=self._config.preemptive_generation,
        )

    async def _wait_for_agent_ready(self, session: AgentSession, timeout_seconds: float) -> None:
        logger_extra = {"timeout_seconds": timeout_seconds}

        timed_out = False
        start_time = time.time()
        while session.agent_state not in _READY_AGENT_STATES and not timed_out:
            self._logger.info(
                "Agent not ready yet.",
                extra={**logger_extra, "agent_state": session.agent_state},
            )
            elapsed_time = time.time() - start_time
            timed_out = elapsed_time > timeout_seconds
            await asyncio.sleep(1.0)

        if timed_out:
            error_message = "Agent failed to start within timeout."
            self._logger.error(error_message, extra=logger_extra)
            raise RuntimeError(error_message)

    async def start_session(
        self,
        call_agent: CallAgent,
        call_room: CallRoom,
        room_input_options: NotGivenOr[room_io.RoomInputOptions] = NOT_GIVEN,
        room_output_options: NotGivenOr[room_io.RoomOutputOptions] = NOT_GIVEN,
    ) -> None:
        logger_extra = {"room_name": call_room.name}
        self._logger.info("Starting call session.", extra=logger_extra)
        self._session = self._create_session()
        await self._session.start(
            room=call_room,
            agent=call_agent,
            room_input_options=room_input_options,
            room_output_options=room_output_options,
        )

        await self._wait_for_agent_ready(
            session=self._session,
            timeout_seconds=self._agent_ready_timeout_seconds,
        )
        self._logger.info("Successfully started call session.", extra=logger_extra)

    async def shutdown(self) -> None:
        self._logger.info("Shutting down.")
        await self.session.aclose()
        self._logger.info("Successfully shut down.")
