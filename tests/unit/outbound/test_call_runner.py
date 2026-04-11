from unittest.mock import AsyncMock, MagicMock

import pytest

from livekit_voice_call_runner.logger import create_logger
from livekit_voice_call_runner.outbound.call_runner import (
    OutboundCallRunner,
    OutboundCallRunnerConfig,
    OutboundCallRunnerProps,
)


@pytest.fixture
def outbound_config():
    return OutboundCallRunnerConfig(
        phone_number_from="+10000000000",
        phone_number_to="+19999999999",
        sip_trunk_id="trunk-123",
        participant_identity="receipent",
        ringing_timeout=10,
        max_call_duration=180,
    )


@pytest.fixture
def mock_props(outbound_config):
    mock_agent = MagicMock()

    mock_room_connector = MagicMock()
    mock_room_connector.room = MagicMock()
    mock_room_connector.room.name = "test-room"
    mock_room_connector.connect = AsyncMock()
    mock_room_connector.shutdown = AsyncMock()

    mock_session_starter = MagicMock()
    mock_session_starter.session = MagicMock()
    mock_session_starter.start_session = AsyncMock()
    mock_session_starter.shutdown = AsyncMock()

    mock_event_listener = MagicMock()
    mock_event_listener.listen_to_room = AsyncMock()
    mock_event_listener.listen_to_session = AsyncMock()
    mock_event_listener.wait_for_shutdown = AsyncMock(
        return_value={"name": "Participant disconnected", "context": {}}
    )

    mock_dialer = MagicMock()
    mock_dialer.dial = AsyncMock()
    mock_dialer.shutdown = AsyncMock()

    logger = create_logger(name="test-runner", correlation_id="test-id")

    return OutboundCallRunnerProps.model_construct(
        call_agent=mock_agent,
        call_room_connector=mock_room_connector,
        call_session_starter=mock_session_starter,
        call_event_listener=mock_event_listener,
        call_dialer=mock_dialer,
        outbound_config=outbound_config,
        logger=logger,
    )


async def test_run(mock_props):
    runner = OutboundCallRunner(props=mock_props)
    await runner.run()

    mock_props.call_room_connector.connect.assert_called_once()
    mock_props.call_dialer.dial.assert_called_once()
    mock_props.call_session_starter.start_session.assert_called_once()


async def test_shutdown_called_even_on_exception(mock_props):
    mock_props.call_room_connector.connect = AsyncMock(side_effect=RuntimeError("connect failed"))

    runner = OutboundCallRunner(props=mock_props)
    await runner.run()  # should not raise

    mock_props.call_session_starter.shutdown.assert_called_once()
    mock_props.call_room_connector.shutdown.assert_called_once()
    mock_props.call_dialer.shutdown.assert_called_once()
