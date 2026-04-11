import functools
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


class ConfigRoomConnector(BaseModel):
    participant_identity: str


class ConfigLiveKit(BaseModel):
    url: str
    api_key: str
    api_secret: str
    room_name_prefix: str


class Config(BaseModel):
    livekit_api: ConfigLiveKit
    call_session: ConfigCallSession
    room_connector: ConfigRoomConnector


def get_env_or_raise(key: str) -> Any:
    value = os.environ.get(key)
    if not value:
        raise ValueError(f"Environment variable {key} is not set")
    return value


def _get_bool(value: str) -> bool:
    return value.lower() in ["true", "1"]


@functools.lru_cache(maxsize=1)
def get_config() -> Config:
    return Config(
        livekit_api=ConfigLiveKit(
            url=get_env_or_raise("LIVEKIT_URL"),
            api_key=get_env_or_raise("LIVEKIT_API_KEY"),
            api_secret=get_env_or_raise("LIVEKIT_API_SECRET"),
            room_name_prefix=get_env_or_raise("LIVEKIT_ROOM_NAME_PREFIX"),
        ),
        call_session=ConfigCallSession(
            llm=ConfigCallSessionLLM(
                azure_deployment=get_env_or_raise("CALL_SESSION_LLM_AZURE_DEPLOYMENT"),
                api_version=get_env_or_raise("CALL_SESSION_LLM_API_VERSION"),
                api_key=get_env_or_raise("CALL_SESSION_LLM_API_KEY"),
                azure_endpoint=get_env_or_raise("CALL_SESSION_LLM_AZURE_ENDPOINT"),
                voice=get_env_or_raise("CALL_SESSION_LLM_VOICE"),
                temperature=float(get_env_or_raise("CALL_SESSION_LLM_TEMPERATURE")),
            ),
            turn_detection=ConfigCallSessionTurnDetection(
                type=get_env_or_raise("CALL_SESSION_LLM_TURN_DETECTION_TYPE"),
                threshold=float(get_env_or_raise("CALL_SESSION_LLM_TURN_DETECTION_THRESHOLD")),
                prefix_padding_ms=int(
                    get_env_or_raise("CALL_SESSION_LLM_TURN_DETECTION_PREFIX_PADDING_MS")
                ),
                silence_duration_ms=int(
                    get_env_or_raise("CALL_SESSION_LLM_TURN_DETECTION_SILENCE_DURATION_MS")
                ),
                create_response=_get_bool(
                    get_env_or_raise("CALL_SESSION_LLM_TURN_DETECTION_CREATE_RESPONSE")
                ),
                interrupt_response=_get_bool(
                    get_env_or_raise("CALL_SESSION_LLM_TURN_DETECTION_INTERRUPT_RESPONSE")
                ),
            ),
            user_away_timeout=float(get_env_or_raise("CALL_SESSION_USER_AWAY_TIMEOUT")),
            use_tts_aligned_transcript=_get_bool(
                get_env_or_raise("CALL_SESSION_USE_TTS_ALIGNED_TRANSCRIPT")
            ),
            preemptive_generation=_get_bool(get_env_or_raise("CALL_SESSION_PREEMPTIVE_GENERATION")),
            agent_ready_timeout_seconds=float(
                get_env_or_raise("CALL_SESSION_AGENT_READY_TIMEOUT_SECONDS")
            ),
        ),
        room_connector=ConfigRoomConnector(
            participant_identity=get_env_or_raise("CALL_ROOM_PARTICIPANT_IDENTITY"),
        ),
    )
