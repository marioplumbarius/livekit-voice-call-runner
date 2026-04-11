import importlib
import sys

import pytest


def _reload_config(module_path: str):
    """Reload a config module and reset its lru_cache so env changes take effect."""
    if module_path in sys.modules:
        del sys.modules[module_path]
    module = importlib.import_module(module_path)
    return module



def test_get_config(shared_env):
    module = _reload_config("livekit_voice_call_runner.config.base")
    cfg = module.get_config()
    assert cfg.livekit_api.url == shared_env["LIVEKIT_URL"]
    assert cfg.livekit_api.api_key == shared_env["LIVEKIT_API_KEY"]
    assert cfg.livekit_api.room_name_prefix == shared_env["LIVEKIT_ROOM_NAME_PREFIX"]
    assert cfg.call_session.llm.voice == shared_env["CALL_SESSION_LLM_VOICE"]
    assert cfg.call_session.turn_detection.create_response is True
    assert cfg.call_session.turn_detection.interrupt_response is False
    assert cfg.room_connector.participant_identity == shared_env["CALL_ROOM_PARTICIPANT_IDENTITY"]


def test_get_config_is_cached(shared_env):
    module = _reload_config("livekit_voice_call_runner.config.base")
    cfg1 = module.get_config()
    cfg2 = module.get_config()
    assert cfg1 is cfg2
