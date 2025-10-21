import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class ConfigCallSessionLLM(BaseModel):
    azure_deployment: str
    api_version: str
    api_key: str
    azure_endpoint: str
    voice: str
    temperature: float


class ConfigCallSessionTurnDetection(BaseModel):
    type: str
    threshold: float
    prefix_padding_ms: int
    silence_duration_ms: int
    create_response: bool
    interrupt_response: bool


class ConfigCallSession(BaseModel):
    llm: ConfigCallSessionLLM
    turn_detection: ConfigCallSessionTurnDetection
    user_away_timeout: float
    use_tts_aligned_transcript: bool
    preemptive_generation: bool
    agent_ready_timeout_seconds: float


class CallOutboundConfig(BaseModel):
    phone_number_from: str
    participant_identity: str
    ringing_timeout: int
    max_call_duration: int


class ConfigRoomConnector(BaseModel):
    participant_identity: str


class ConfigLiveKit(BaseModel):
    url: str
    api_key: str
    api_secret: str
    room_name_prefix: str
    outbound_sip_trunk_id: str


class ConfigModel(BaseModel):
    livekit_api: ConfigLiveKit
    call_session: ConfigCallSession
    call_outbound_config: CallOutboundConfig
    room_connector: ConfigRoomConnector


def _get_env_or_raise(key: str) -> Any:
    value = os.environ.get(key)
    if not value:
        raise ValueError(f"Environment variable {key} is not set")
    return value


def _get_bool(value: str) -> bool:
    return value.lower() in ["true", "1"]


Config = ConfigModel(
    livekit_api=ConfigLiveKit(
        url=_get_env_or_raise("LIVEKIT_URL"),
        api_key=_get_env_or_raise("LIVEKIT_API_KEY"),
        api_secret=_get_env_or_raise("LIVEKIT_API_SECRET"),
        room_name_prefix=_get_env_or_raise("LIVEKIT_ROOM_NAME_PREFIX"),
        outbound_sip_trunk_id=_get_env_or_raise("LIVEKIT_OUTBOUND_SIP_TRUNK_ID"),
    ),
    call_session=ConfigCallSession(
        llm=ConfigCallSessionLLM(
            azure_deployment=_get_env_or_raise("CALL_SESSION_LLM_AZURE_DEPLOYMENT"),
            api_version=_get_env_or_raise("CALL_SESSION_LLM_API_VERSION"),
            api_key=_get_env_or_raise("CALL_SESSION_LLM_API_KEY"),
            azure_endpoint=_get_env_or_raise("CALL_SESSION_LLM_AZURE_ENDPOINT"),
            voice=_get_env_or_raise("CALL_SESSION_LLM_VOICE"),
            temperature=float(_get_env_or_raise("CALL_SESSION_LLM_TEMPERATURE")),
        ),
        turn_detection=ConfigCallSessionTurnDetection(
            type=_get_env_or_raise("CALL_SESSION_LLM_TURN_DETECTION_TYPE"),
            threshold=float(_get_env_or_raise("CALL_SESSION_LLM_TURN_DETECTION_THRESHOLD")),
            prefix_padding_ms=int(_get_env_or_raise("CALL_SESSION_LLM_TURN_DETECTION_PREFIX_PADDING_MS")),
            silence_duration_ms=int(_get_env_or_raise("CALL_SESSION_LLM_TURN_DETECTION_SILENCE_DURATION_MS")),
            create_response=_get_bool(_get_env_or_raise("CALL_SESSION_LLM_TURN_DETECTION_CREATE_RESPONSE")),
            interrupt_response=_get_bool(_get_env_or_raise("CALL_SESSION_LLM_TURN_DETECTION_INTERRUPT_RESPONSE")),
        ),
        user_away_timeout=float(_get_env_or_raise("CALL_SESSION_USER_AWAY_TIMEOUT")),
        use_tts_aligned_transcript=_get_bool(_get_env_or_raise("CALL_SESSION_USE_TTS_ALIGNED_TRANSCRIPT")),
        preemptive_generation=_get_bool(_get_env_or_raise("CALL_SESSION_PREEMPTIVE_GENERATION")),
        agent_ready_timeout_seconds=float(_get_env_or_raise("CALL_SESSION_AGENT_READY_TIMEOUT_SECONDS")),
    ),
    call_outbound_config=CallOutboundConfig(
        phone_number_from=_get_env_or_raise("CALL_OUTBOUND_PHONE_NUMBER_FROM"),
        participant_identity=_get_env_or_raise("CALL_OUTBOUND_PARTICIPANT_IDENTITY"),
        ringing_timeout=int(_get_env_or_raise("CALL_OUTBOUND_RINGING_TIMEOUT")),
        max_call_duration=int(_get_env_or_raise("CALL_OUTBOUND_MAX_CALL_DURATION")),
    ),
    room_connector=ConfigRoomConnector(
        participant_identity=_get_env_or_raise("CALL_ROOM_PARTICIPANT_IDENTITY"),
    ),
)
