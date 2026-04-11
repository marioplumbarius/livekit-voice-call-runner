def test_get_config(outbound_env, reload_config):
    cfg = reload_config("livekit_voice_call_runner.config.outbound").get_config()
    assert cfg.sip_trunk_id == outbound_env["LIVEKIT_OUTBOUND_SIP_TRUNK_ID"]
    assert cfg.phone_number_from == outbound_env["CALL_OUTBOUND_PHONE_NUMBER_FROM"]
    assert cfg.ringing_timeout == int(outbound_env["CALL_OUTBOUND_RINGING_TIMEOUT"])
    assert cfg.max_call_duration == int(outbound_env["CALL_OUTBOUND_MAX_CALL_DURATION"])
