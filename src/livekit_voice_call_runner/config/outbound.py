import os
from typing import Any, Optional

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class OutboundConfig(BaseModel):
    sip_trunk_id: str
    phone_number_from: str
    participant_identity: str
    ringing_timeout: int
    max_call_duration: int


def _get_env_or_raise(key: str) -> Any:
    value = os.environ.get(key)
    if not value:
        raise ValueError(f"Environment variable {key} is not set")
    return value


_config: Optional[OutboundConfig] = None


def get_config() -> OutboundConfig:
    global _config
    if _config is None:
        _config = OutboundConfig(
            sip_trunk_id=_get_env_or_raise("LIVEKIT_OUTBOUND_SIP_TRUNK_ID"),
            phone_number_from=_get_env_or_raise("CALL_OUTBOUND_PHONE_NUMBER_FROM"),
            participant_identity=_get_env_or_raise("CALL_OUTBOUND_PARTICIPANT_IDENTITY"),
            ringing_timeout=int(_get_env_or_raise("CALL_OUTBOUND_RINGING_TIMEOUT")),
            max_call_duration=int(_get_env_or_raise("CALL_OUTBOUND_MAX_CALL_DURATION")),
        )
    return _config
