from livekit import api
from livekit.plugins import openai
from openai.types.beta.realtime.session import TurnDetection

from livekit_voice_call_runner.config import outbound as outbound_config_module
from livekit_voice_call_runner.config import shared as shared_config_module
from livekit_voice_call_runner.core.call_agent import CallAgent
from livekit_voice_call_runner.core.call_event_listener import CallEventListener
from livekit_voice_call_runner.core.call_session_starter import CallSessionStarter
from livekit_voice_call_runner.logger import CallLogger, create_logger
from livekit_voice_call_runner.model import CallSessionStarterConfigRealtime
from livekit_voice_call_runner.outbound.call_dialer import CallDialer
from livekit_voice_call_runner.outbound.call_room_connector import CallRoomConnector
from livekit_voice_call_runner.outbound.call_runner import CallRunner, CallRunnerOutboundConfig, CallRunnerProps


def _create_livekit_api() -> api.LiveKitAPI:
    cfg = shared_config_module.get_config()
    return api.LiveKitAPI(
        url=cfg.livekit_api.url,
        api_key=cfg.livekit_api.api_key,
        api_secret=cfg.livekit_api.api_secret,
    )


def create_call_agent(instructions: str, correlation_id: str) -> CallAgent:
    return CallAgent(
        instructions=instructions,
        logger=create_logger(name=CallAgent.__name__, correlation_id=correlation_id),
    )


def _create_call_session_starter(logger: CallLogger) -> CallSessionStarter:
    cfg = shared_config_module.get_config()
    return CallSessionStarter(
        config=CallSessionStarterConfigRealtime(
            llm=openai.realtime.RealtimeModel.with_azure(
                azure_deployment=cfg.call_session.llm.azure_deployment,
                api_version=cfg.call_session.llm.api_version,
                api_key=cfg.call_session.llm.api_key,
                azure_endpoint=cfg.call_session.llm.azure_endpoint,
                voice=cfg.call_session.llm.voice,
                temperature=cfg.call_session.llm.temperature,
                turn_detection=TurnDetection(
                    type=cfg.call_session.turn_detection.type,  # type: ignore
                    threshold=cfg.call_session.turn_detection.threshold,
                    prefix_padding_ms=cfg.call_session.turn_detection.prefix_padding_ms,
                    silence_duration_ms=cfg.call_session.turn_detection.silence_duration_ms,
                    create_response=cfg.call_session.turn_detection.create_response,
                    interrupt_response=cfg.call_session.turn_detection.interrupt_response,
                ),
            ),
            user_away_timeout=cfg.call_session.user_away_timeout,
            use_tts_aligned_transcript=cfg.call_session.use_tts_aligned_transcript,
            preemptive_generation=cfg.call_session.preemptive_generation,
        ),
        agent_ready_timeout_seconds=cfg.call_session.agent_ready_timeout_seconds,
        logger=logger,
    )


def create_call_session_starter(correlation_id: str) -> CallSessionStarter:
    return _create_call_session_starter(
        logger=create_logger(name=CallSessionStarter.__name__, correlation_id=correlation_id)
    )


def create_call_event_listener(correlation_id: str) -> CallEventListener:
    return CallEventListener(
        logger=create_logger(name=CallEventListener.__name__, correlation_id=correlation_id)
    )


def create_call_runner_props(
    instructions: str,
    phone_number_to: str,
    correlation_id: str,
) -> CallRunnerProps:
    cfg = shared_config_module.get_config()
    outbound_cfg = outbound_config_module.get_config()
    livekit_api = _create_livekit_api()
    return CallRunnerProps(
        call_agent=create_call_agent(instructions=instructions, correlation_id=correlation_id),
        call_room_connector=CallRoomConnector(
            participant_identity=cfg.room_connector.participant_identity,
            room_name_prefix=cfg.livekit_api.room_name_prefix,
            livekit_url=cfg.livekit_api.url,
            livekit_api=livekit_api,
            logger=create_logger(name=CallRoomConnector.__name__, correlation_id=correlation_id),
        ),
        call_session_starter=create_call_session_starter(correlation_id=correlation_id),
        call_event_listener=create_call_event_listener(correlation_id=correlation_id),
        call_dialer=CallDialer(
            livekit_api=livekit_api,
            logger=create_logger(name=CallDialer.__name__, correlation_id=correlation_id),
        ),
        outbound_config=CallRunnerOutboundConfig(
            phone_number_from=outbound_cfg.phone_number_from,
            phone_number_to=phone_number_to,
            sip_trunk_id=outbound_cfg.sip_trunk_id,
            participant_identity=outbound_cfg.participant_identity,
            ringing_timeout=outbound_cfg.ringing_timeout,
            max_call_duration=outbound_cfg.max_call_duration,
        ),
        logger=create_logger(name=CallRunner.__name__, correlation_id=correlation_id),
    )
