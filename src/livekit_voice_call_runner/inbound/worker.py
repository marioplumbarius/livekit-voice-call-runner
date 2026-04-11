import sys
import uuid

from livekit.agents import JobContext, WorkerOptions, cli

from livekit_voice_call_runner import factory
from livekit_voice_call_runner.config import shared as shared_config
from livekit_voice_call_runner.logger import create_logger

logger = create_logger(name=__name__)


def _make_entrypoint(instructions: str):
    async def entrypoint(ctx: JobContext) -> None:
        correlation_id = str(uuid.uuid4())
        log = create_logger(name="inbound.entrypoint", correlation_id=correlation_id)

        await ctx.connect()

        log.info("Inbound call received.", extra={"room": ctx.room.name})

        cfg = shared_config.get_config()
        call_agent = factory.create_call_inbound_agent(instructions=instructions, correlation_id=correlation_id)
        call_session_starter = factory.create_call_session_starter(correlation_id=correlation_id, cfg=cfg)
        call_event_listener = factory.create_call_event_listener(correlation_id=correlation_id)

        await call_event_listener.listen_to_room(room=ctx.room)
        await call_session_starter.start_session(call_agent=call_agent, call_room=ctx.room)
        await call_event_listener.listen_to_session(
            session=call_session_starter.session, agent=call_agent
        )

        try:
            await call_event_listener.wait_for_shutdown()
        finally:
            await call_session_starter.shutdown()
            log.info("Inbound call ended.")

    return entrypoint


def run(instructions: str) -> None:
    # Force the LiveKit agents worker into dev mode, bypassing the livekit CLI sub-command requirement.
    sys.argv = [sys.argv[0], "dev"]
    cli.run_app(WorkerOptions(entrypoint_fnc=_make_entrypoint(instructions)))
