import importlib
import sys

import pytest


def _reload_config(module_path: str):
    """Reload a config module and reset its lru_cache so env changes take effect."""
    if module_path in sys.modules:
        del sys.modules[module_path]
    module = importlib.import_module(module_path)
    return module


def test_get_config_when_required_var_missing(monkeypatch):
    monkeypatch.delenv("LIVEKIT_OUTBOUND_SIP_TRUNK_ID", raising=False)
    module = _reload_config("livekit_voice_call_runner.config.outbound")
    with pytest.raises(ValueError, match="LIVEKIT_OUTBOUND_SIP_TRUNK_ID"):
        module.get_config()


def test_get_config_succeeds(outbound_env):
    module = _reload_config("livekit_voice_call_runner.config.outbound")
    cfg = module.get_config()
    assert cfg.sip_trunk_id == outbound_env["LIVEKIT_OUTBOUND_SIP_TRUNK_ID"]
    assert cfg.phone_number_from == outbound_env["CALL_OUTBOUND_PHONE_NUMBER_FROM"]
    assert cfg.ringing_timeout == int(outbound_env["CALL_OUTBOUND_RINGING_TIMEOUT"])
    assert cfg.max_call_duration == int(outbound_env["CALL_OUTBOUND_MAX_CALL_DURATION"])


def test_get_config_does_not_require_base_vars(monkeypatch, outbound_env):
    """Outbound config should load independently of base env vars."""
    monkeypatch.delenv("LIVEKIT_URL", raising=False)
    monkeypatch.delenv("CALL_SESSION_LLM_API_KEY", raising=False)
    module = _reload_config("livekit_voice_call_runner.config.outbound")
    cfg = module.get_config()
    assert cfg.sip_trunk_id == outbound_env["LIVEKIT_OUTBOUND_SIP_TRUNK_ID"]
