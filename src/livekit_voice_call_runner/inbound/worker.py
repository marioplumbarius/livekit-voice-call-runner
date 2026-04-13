import uuid

from livekit.agents import JobContext

from livekit_voice_call_runner import config, factory
from livekit_voice_call_runner.logger import create_logger

logger = create_logger(name=__name__)


async def handle(ctx: JobContext, instructions: str) -> None:
    correlation_id = str(uuid.uuid4())
    log = create_logger(name="inbound.entrypoint", correlation_id=correlation_id)

    await ctx.connect()

    log.info("Inbound call received.", extra={"room": ctx.room.name})

    cfg = config.base.get_config()
    call_agent = factory.create_call_agent(instructions=instructions, correlation_id=correlation_id)
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
