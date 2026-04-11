import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _patch_entrypoint_deps(mocker, mock_agent, mock_session_starter, mock_event_listener):
    mocker.patch("livekit_voice_call_runner.inbound.worker.shared_config")
    mocker.patch(
        "livekit_voice_call_runner.factory.create_call_inbound_agent", return_value=mock_agent
    )
    mocker.patch(
        "livekit_voice_call_runner.factory.create_call_session_starter",
        return_value=mock_session_starter,
    )
    mocker.patch(
        "livekit_voice_call_runner.factory.create_call_event_listener",
        return_value=mock_event_listener,
    )


async def test_entrypoint_calls_ctx_connect_first(mocker):
    """ctx.connect() must be called before any factory or session calls."""
    call_order = []

    mock_ctx = MagicMock()
    mock_ctx.room = MagicMock()
    mock_ctx.room.name = "test-room"
    mock_ctx.connect = AsyncMock(side_effect=lambda: call_order.append("connect"))

    mock_agent = MagicMock()
    mock_session_starter = MagicMock()
    mock_session_starter.start_session = AsyncMock(
        side_effect=lambda **_: call_order.append("start_session")
    )
    mock_session_starter.session = MagicMock()
    mock_session_starter.shutdown = AsyncMock()

    mock_event_listener = MagicMock()
    mock_event_listener.listen_to_room = AsyncMock(
        side_effect=lambda **_: call_order.append("listen_to_room")
    )
    mock_event_listener.listen_to_session = AsyncMock()
    mock_event_listener.wait_for_shutdown = AsyncMock(return_value={"name": "ended"})

    _patch_entrypoint_deps(mocker, mock_agent, mock_session_starter, mock_event_listener)

    from livekit_voice_call_runner.inbound.worker import _make_entrypoint

    entrypoint = _make_entrypoint(instructions="Test instructions")
    await entrypoint(mock_ctx)

    assert call_order[0] == "connect"
    assert "listen_to_room" in call_order
    assert "start_session" in call_order


async def test_entrypoint_calls_shutdown_in_finally(mocker):
    """shutdown must be called even if wait_for_shutdown raises."""
    mock_ctx = MagicMock()
    mock_ctx.room = MagicMock()
    mock_ctx.room.name = "test-room"
    mock_ctx.connect = AsyncMock()

    mock_agent = MagicMock()
    mock_session_starter = MagicMock()
    mock_session_starter.start_session = AsyncMock()
    mock_session_starter.session = MagicMock()
    mock_session_starter.shutdown = AsyncMock()

    mock_event_listener = MagicMock()
    mock_event_listener.listen_to_room = AsyncMock()
    mock_event_listener.listen_to_session = AsyncMock()
    mock_event_listener.wait_for_shutdown = AsyncMock(
        side_effect=RuntimeError("session error")
    )

    _patch_entrypoint_deps(mocker, mock_agent, mock_session_starter, mock_event_listener)

    from livekit_voice_call_runner.inbound.worker import _make_entrypoint

    entrypoint = _make_entrypoint(instructions="Test instructions")

    with pytest.raises(RuntimeError, match="session error"):
        await entrypoint(mock_ctx)

    mock_session_starter.shutdown.assert_called_once()


def test_run_sets_dev_argv(mocker):
    """run must inject 'dev' into sys.argv before calling cli.run_app."""
    mock_run_app = mocker.patch("livekit.agents.cli.run_app")

    from livekit_voice_call_runner.inbound.worker import run

    original_argv = sys.argv.copy()
    run(instructions="Test instructions")

    mock_run_app.assert_called_once()
    assert sys.argv[1] == "dev"

    sys.argv = original_argv


async def test_entrypoint_passes_rtc_room_to_listen_to_room(mocker):
    """listen_to_room must receive ctx.room (plain rtc.Room), not a CallRoom."""
    mock_ctx = MagicMock()
    mock_ctx.room = MagicMock()
    mock_ctx.room.name = "test-room"
    mock_ctx.connect = AsyncMock()

    mock_agent = MagicMock()
    mock_session_starter = MagicMock()
    mock_session_starter.start_session = AsyncMock()
    mock_session_starter.session = MagicMock()
    mock_session_starter.shutdown = AsyncMock()

    mock_event_listener = MagicMock()
    mock_event_listener.listen_to_room = AsyncMock()
    mock_event_listener.listen_to_session = AsyncMock()
    mock_event_listener.wait_for_shutdown = AsyncMock(return_value={"name": "ended"})

    _patch_entrypoint_deps(mocker, mock_agent, mock_session_starter, mock_event_listener)

    from livekit_voice_call_runner.inbound.worker import _make_entrypoint

    entrypoint = _make_entrypoint(instructions="Test instructions")
    await entrypoint(mock_ctx)

    mock_event_listener.listen_to_room.assert_called_once_with(room=mock_ctx.room)
    mock_session_starter.start_session.assert_called_once_with(
        call_agent=mock_agent, call_room=mock_ctx.room
    )
