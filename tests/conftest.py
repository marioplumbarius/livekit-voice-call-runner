import pytest

from livekit_voice_call_runner.logger import create_logger


@pytest.fixture
def mock_logger(mocker):
    logger = create_logger(name="test", correlation_id="test-correlation-id")
    mocker.patch.object(logger, "info")
    mocker.patch.object(logger, "error")
    mocker.patch.object(logger, "warning")
    return logger


@pytest.fixture
def shared_env(monkeypatch):
    """Set all shared env vars required by config/shared.py."""
    vars = {
        "LIVEKIT_URL": "wss://test.livekit.cloud",
        "LIVEKIT_API_KEY": "test-api-key",
        "LIVEKIT_API_SECRET": "test-api-secret",
        "LIVEKIT_ROOM_NAME_PREFIX": "test-room",
        "CALL_SESSION_LLM_AZURE_DEPLOYMENT": "gpt-4o-realtime",
        "CALL_SESSION_LLM_API_VERSION": "2024-10-01-preview",
        "CALL_SESSION_LLM_API_KEY": "test-llm-key",
        "CALL_SESSION_LLM_AZURE_ENDPOINT": "https://test.openai.azure.com",
        "CALL_SESSION_LLM_VOICE": "alloy",
        "CALL_SESSION_LLM_TEMPERATURE": "0.7",
        "CALL_SESSION_LLM_TURN_DETECTION_TYPE": "server_vad",
        "CALL_SESSION_LLM_TURN_DETECTION_THRESHOLD": "0.3",
        "CALL_SESSION_LLM_TURN_DETECTION_PREFIX_PADDING_MS": "300",
        "CALL_SESSION_LLM_TURN_DETECTION_SILENCE_DURATION_MS": "500",
        "CALL_SESSION_LLM_TURN_DETECTION_CREATE_RESPONSE": "True",
        "CALL_SESSION_LLM_TURN_DETECTION_INTERRUPT_RESPONSE": "False",
        "CALL_SESSION_USER_AWAY_TIMEOUT": "10",
        "CALL_SESSION_USE_TTS_ALIGNED_TRANSCRIPT": "True",
        "CALL_SESSION_PREEMPTIVE_GENERATION": "True",
        "CALL_SESSION_AGENT_READY_TIMEOUT_SECONDS": "5",
        "CALL_ROOM_PARTICIPANT_IDENTITY": "caller",
    }
    for key, value in vars.items():
        monkeypatch.setenv(key, value)
    return vars


@pytest.fixture
def outbound_env(monkeypatch):
    """Set all outbound-specific env vars required by config/outbound.py."""
    vars = {
        "LIVEKIT_OUTBOUND_SIP_TRUNK_ID": "trunk-123",
        "CALL_OUTBOUND_PHONE_NUMBER_FROM": "+10000000000",
        "CALL_OUTBOUND_PARTICIPANT_IDENTITY": "receipent",
        "CALL_OUTBOUND_RINGING_TIMEOUT": "10",
        "CALL_OUTBOUND_MAX_CALL_DURATION": "180",
    }
    for key, value in vars.items():
        monkeypatch.setenv(key, value)
    return vars
