import importlib
import sys

import pytest


def _reload_config(module_path: str):
    """Reload a config module and reset its lru_cache so env changes take effect."""
    if module_path in sys.modules:
        del sys.modules[module_path]
    module = importlib.import_module(module_path)
    return module


def test_shared_importing_module_does_not_raise_without_env_vars():
    """Importing config.shared must not raise even if no env vars are set."""
    _reload_config("livekit_voice_call_runner.config.shared")


def test_shared_get_config_raises_when_required_var_missing(monkeypatch):
    monkeypatch.delenv("LIVEKIT_URL", raising=False)
    module = _reload_config("livekit_voice_call_runner.config.shared")
    with pytest.raises(ValueError, match="LIVEKIT_URL"):
        module.get_config()


def test_shared_get_config_returns_correct_values(shared_env):
    module = _reload_config("livekit_voice_call_runner.config.shared")
    cfg = module.get_config()
    assert cfg.livekit_api.url == shared_env["LIVEKIT_URL"]
    assert cfg.livekit_api.api_key == shared_env["LIVEKIT_API_KEY"]
    assert cfg.livekit_api.room_name_prefix == shared_env["LIVEKIT_ROOM_NAME_PREFIX"]
    assert cfg.call_session.llm.voice == shared_env["CALL_SESSION_LLM_VOICE"]
    assert cfg.call_session.turn_detection.create_response is True
    assert cfg.call_session.turn_detection.interrupt_response is False
    assert cfg.room_connector.participant_identity == shared_env["CALL_ROOM_PARTICIPANT_IDENTITY"]


def test_shared_get_config_is_cached(shared_env):
    module = _reload_config("livekit_voice_call_runner.config.shared")
    cfg1 = module.get_config()
    cfg2 = module.get_config()
    assert cfg1 is cfg2


def test_outbound_importing_module_does_not_raise_without_env_vars():
    """Importing config.outbound must not raise even if no outbound env vars are set."""
    _reload_config("livekit_voice_call_runner.config.outbound")


def test_outbound_get_config_raises_when_required_var_missing(monkeypatch):
    monkeypatch.delenv("LIVEKIT_OUTBOUND_SIP_TRUNK_ID", raising=False)
    module = _reload_config("livekit_voice_call_runner.config.outbound")
    with pytest.raises(ValueError, match="LIVEKIT_OUTBOUND_SIP_TRUNK_ID"):
        module.get_config()


def test_outbound_get_config_returns_correct_values(outbound_env):
    module = _reload_config("livekit_voice_call_runner.config.outbound")
    cfg = module.get_config()
    assert cfg.sip_trunk_id == outbound_env["LIVEKIT_OUTBOUND_SIP_TRUNK_ID"]
    assert cfg.phone_number_from == outbound_env["CALL_OUTBOUND_PHONE_NUMBER_FROM"]
    assert cfg.ringing_timeout == int(outbound_env["CALL_OUTBOUND_RINGING_TIMEOUT"])
    assert cfg.max_call_duration == int(outbound_env["CALL_OUTBOUND_MAX_CALL_DURATION"])


def test_outbound_config_does_not_require_shared_vars(monkeypatch, outbound_env):
    """Outbound config should load independently of shared env vars."""
    monkeypatch.delenv("LIVEKIT_URL", raising=False)
    monkeypatch.delenv("CALL_SESSION_LLM_API_KEY", raising=False)
    module = _reload_config("livekit_voice_call_runner.config.outbound")
    cfg = module.get_config()
    assert cfg.sip_trunk_id == outbound_env["LIVEKIT_OUTBOUND_SIP_TRUNK_ID"]
