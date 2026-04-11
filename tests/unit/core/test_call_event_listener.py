import asyncio

import pytest
from unittest.mock import MagicMock, AsyncMock

from livekit_voice_call_runner.core.call_event_listener import CallEventListener
from livekit_voice_call_runner.logger import create_logger


@pytest.fixture
def listener():
    logger = create_logger(name="test-listener", correlation_id="test-id")
    return CallEventListener(logger=logger)


class TestCallEventListener:
    async def test_listen_to_room_accepts_rtc_room(self, listener, mocker):
        """listen_to_room must accept a plain rtc.Room (widened type)."""
        mock_room = MagicMock()
        mock_room.name = "test-room"
        mock_room.on = MagicMock(return_value=lambda fn: fn)

        # Should not raise — the widened type accepts rtc.Room
        await listener.listen_to_room(room=mock_room)

    async def test_shutdown_triggered_on_participant_disconnect(self, listener, mocker):
        mock_room = MagicMock()
        mock_room.name = "test-room"

        handlers = {}

        def capture_on(event):
            def decorator(fn):
                handlers[event] = fn
                return fn

            return decorator

        mock_room.on = capture_on

        await listener.listen_to_room(room=mock_room)

        # Simulate participant disconnect
        mock_participant = MagicMock()
        mock_participant.identity = "caller-participant"
        handlers["participant_disconnected"](mock_participant)

        result = await listener.wait_for_shutdown()
        assert "name" in result or isinstance(result, dict)

    async def test_shutdown_triggered_on_room_disconnected(self, listener, mocker):
        from livekit import rtc

        mock_room = MagicMock()
        mock_room.name = "test-room"

        handlers = {}

        def capture_on(event):
            def decorator(fn):
                handlers[event] = fn
                return fn

            return decorator

        mock_room.on = capture_on

        await listener.listen_to_room(room=mock_room)

        handlers["disconnected"](rtc.DisconnectReason.UNKNOWN_REASON)

        result = await listener.wait_for_shutdown()
        assert isinstance(result, dict)

    async def test_session_error_triggers_shutdown(self, listener, mocker):
        mock_session = MagicMock()
        mock_agent = MagicMock()

        handlers = {}

        def capture_on(event):
            def decorator(fn):
                handlers[event] = fn
                return fn

            return decorator

        mock_session.on = capture_on

        await listener.listen_to_session(session=mock_session, agent=mock_agent)

        mock_error_event = MagicMock()
        mock_error_event.model_dump.return_value = {"error": "test error"}
        handlers["error"](mock_error_event)

        result = await listener.wait_for_shutdown()
        assert isinstance(result, dict)
