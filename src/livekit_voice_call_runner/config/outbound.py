import functools

from dotenv import load_dotenv
from pydantic import BaseModel

from livekit_voice_call_runner.config.shared import get_env_or_raise

load_dotenv()


class OutboundConfig(BaseModel):
    sip_trunk_id: str
    phone_number_from: str
    participant_identity: str
    ringing_timeout: int
    max_call_duration: int


@functools.lru_cache(maxsize=1)
def get_config() -> OutboundConfig:
    return OutboundConfig(
        sip_trunk_id=get_env_or_raise("LIVEKIT_OUTBOUND_SIP_TRUNK_ID"),
        phone_number_from=get_env_or_raise("CALL_OUTBOUND_PHONE_NUMBER_FROM"),
        participant_identity=get_env_or_raise("CALL_OUTBOUND_PARTICIPANT_IDENTITY"),
        ringing_timeout=int(get_env_or_raise("CALL_OUTBOUND_RINGING_TIMEOUT")),
        max_call_duration=int(get_env_or_raise("CALL_OUTBOUND_MAX_CALL_DURATION")),
    )
