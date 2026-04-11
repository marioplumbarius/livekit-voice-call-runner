import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from livekit_voice_call_runner.core.call_session_starter import CallSessionStarter
from livekit_voice_call_runner.logger import create_logger
from livekit_voice_call_runner.model import CallSessionStarterConfigRealtime


@pytest.fixture
def mock_config(mocker):
    config = MagicMock(spec=CallSessionStarterConfigRealtime)
    config.llm = MagicMock()
    config.user_away_timeout = 10.0
    config.use_tts_aligned_transcript = True
    config.preemptive_generation = True
    return config


@pytest.fixture
def starter(mock_config):
    logger = create_logger(name="test-starter", correlation_id="test-id")
    return CallSessionStarter(
        config=mock_config,
        agent_ready_timeout_seconds=5.0,
        logger=logger,
    )


class TestCallSessionStarter:
    def test_session_property_raises_before_start(self, starter):
        with pytest.raises(RuntimeError, match="Session not started"):
            _ = starter.session

    async def test_start_session_accepts_rtc_room(self, starter, mocker):
        """start_session must accept a plain rtc.Room (widened type)."""
        mock_room = MagicMock()
        mock_room.name = "test-room"

        mock_session = MagicMock()
        mock_session.agent_state = "listening"
        mock_session.start = AsyncMock()

        mocker.patch.object(starter, "_create_session", return_value=mock_session)

        mock_agent = MagicMock()

        await starter.start_session(call_agent=mock_agent, call_room=mock_room)
        assert starter.session is mock_session

    async def test_start_session_raises_on_timeout(self, starter, mocker):
        mock_room = MagicMock()
        mock_room.name = "test-room"

        mock_session = MagicMock()
        mock_session.agent_state = "initializing"  # never becomes ready
        mock_session.start = AsyncMock()

        mocker.patch.object(starter, "_create_session", return_value=mock_session)
        mocker.patch("asyncio.sleep", new_callable=AsyncMock)

        # With a tiny timeout it should eventually raise
        starter._agent_ready_timeout_seconds = 0.0
        mock_agent = MagicMock()

        with pytest.raises(RuntimeError, match="Agent failed to start within timeout"):
            await starter.start_session(call_agent=mock_agent, call_room=mock_room)

    async def test_shutdown_closes_session(self, starter, mocker):
        mock_session = MagicMock()
        mock_session.agent_state = "listening"
        mock_session.start = AsyncMock()
        mock_session.aclose = AsyncMock()

        mocker.patch.object(starter, "_create_session", return_value=mock_session)
        mock_agent = MagicMock()
        mock_room = MagicMock()
        mock_room.name = "test-room"

        await starter.start_session(call_agent=mock_agent, call_room=mock_room)
        await starter.shutdown()

        mock_session.aclose.assert_called_once()
