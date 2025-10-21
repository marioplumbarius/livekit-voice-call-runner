from livekit import api
from livekit.plugins import openai
from openai.types.beta.realtime.session import TurnDetection

from livekit_voice_call_runner.config import Config
from livekit_voice_call_runner.core.call_agent import CallAgent
from livekit_voice_call_runner.core.call_dialer import CallDialer
from livekit_voice_call_runner.core.call_event_listener import CallEventListener
from livekit_voice_call_runner.core.call_room_connector import CallRoomConnector
from livekit_voice_call_runner.core.call_runner import CallRunner, CallRunnerOutboundConfig, CallRunnerProps
from livekit_voice_call_runner.core.call_session_starter import CallSessionStarter
from livekit_voice_call_runner.logger import CallLogger, create_logger
from livekit_voice_call_runner.model import CallSessionStarterConfigRealtime


def _create_livekit_api() -> api.LiveKitAPI:
    return api.LiveKitAPI(
        url=Config.livekit_api.url,
        api_key=Config.livekit_api.api_key,
        api_secret=Config.livekit_api.api_secret,
    )


def _create_call_room_connector(livekit_api: api.LiveKitAPI, logger: CallLogger) -> CallRoomConnector:
    return CallRoomConnector(
        participant_identity=Config.room_connector.participant_identity,
        room_name_prefix=Config.livekit_api.room_name_prefix,
        livekit_url=Config.livekit_api.url,
        livekit_api=livekit_api,
        logger=logger,
    )


def _create_call_session_starter(logger: CallLogger) -> CallSessionStarter:
    return CallSessionStarter(
        config=CallSessionStarterConfigRealtime(
            llm=openai.realtime.RealtimeModel.with_azure(
                azure_deployment=Config.call_session.llm.azure_deployment,
                api_version=Config.call_session.llm.api_version,
                api_key=Config.call_session.llm.api_key,
                azure_endpoint=Config.call_session.llm.azure_endpoint,
                voice=Config.call_session.llm.voice,
                temperature=Config.call_session.llm.temperature,
                turn_detection=TurnDetection(
                    type=Config.call_session.turn_detection.type,  # type: ignore
                    threshold=Config.call_session.turn_detection.threshold,
                    prefix_padding_ms=Config.call_session.turn_detection.prefix_padding_ms,
                    silence_duration_ms=Config.call_session.turn_detection.silence_duration_ms,
                    create_response=Config.call_session.turn_detection.create_response,
                    interrupt_response=Config.call_session.turn_detection.interrupt_response,
                ),
            ),
            user_away_timeout=Config.call_session.user_away_timeout,
            use_tts_aligned_transcript=Config.call_session.use_tts_aligned_transcript,
            preemptive_generation=Config.call_session.preemptive_generation,
        ),
        agent_ready_timeout_seconds=Config.call_session.agent_ready_timeout_seconds,
        logger=logger,
    )


def _create_call_runner_outbound_config(phone_number_to: str) -> CallRunnerOutboundConfig:
    return CallRunnerOutboundConfig(
        phone_number_from=Config.call_outbound_config.phone_number_from,
        phone_number_to=phone_number_to,
        sip_trunk_id=Config.livekit_api.outbound_sip_trunk_id,
        participant_identity=Config.call_outbound_config.participant_identity,
        ringing_timeout=Config.call_outbound_config.ringing_timeout,
        max_call_duration=Config.call_outbound_config.max_call_duration,
    )


def create_call_runner_props(
    instructions: str,
    phone_number_to: str,
    correlation_id: str,
) -> CallRunnerProps:
    livekit_api = _create_livekit_api()
    return CallRunnerProps(
        call_agent=CallAgent(
            instructions=instructions,
            logger=create_logger(name=CallAgent.__name__, correlation_id=correlation_id),
        ),
        call_room_connector=_create_call_room_connector(
            livekit_api=livekit_api,
            logger=create_logger(name=CallRoomConnector.__name__, correlation_id=correlation_id),
        ),
        call_session_starter=_create_call_session_starter(
            logger=create_logger(name=CallSessionStarter.__name__, correlation_id=correlation_id)
        ),
        call_event_listener=CallEventListener(
            logger=create_logger(name=CallEventListener.__name__, correlation_id=correlation_id)
        ),
        call_dialer=CallDialer(
            livekit_api=livekit_api,
            logger=create_logger(name=CallDialer.__name__, correlation_id=correlation_id),
        ),
        outbound_config=_create_call_runner_outbound_config(phone_number_to=phone_number_to),
        logger=create_logger(name=CallRunner.__name__, correlation_id=correlation_id),
    )
