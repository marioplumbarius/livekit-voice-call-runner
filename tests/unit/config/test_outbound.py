import importlib
import sys

import pytest


def _reload_config(module_path: str):
    """Reload a config module and reset its lru_cache so env changes take effect."""
    if module_path in sys.modules:
        del sys.modules[module_path]
    module = importlib.import_module(module_path)
    return module



def test_get_config(outbound_env):
    module = _reload_config("livekit_voice_call_runner.config.outbound")
    cfg = module.get_config()
    assert cfg.sip_trunk_id == outbound_env["LIVEKIT_OUTBOUND_SIP_TRUNK_ID"]
    assert cfg.phone_number_from == outbound_env["CALL_OUTBOUND_PHONE_NUMBER_FROM"]
    assert cfg.ringing_timeout == int(outbound_env["CALL_OUTBOUND_RINGING_TIMEOUT"])
    assert cfg.max_call_duration == int(outbound_env["CALL_OUTBOUND_MAX_CALL_DURATION"])


