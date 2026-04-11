import asyncio
import sys
import uuid

from livekit_voice_call_runner.concurrency.tasks_runner import ConcurrentTasksRunner
from livekit_voice_call_runner.logger import create_logger
from livekit_voice_call_runner.outbound.call_orchestrator import CallOrchestrator

logger = create_logger(name=__name__, correlation_id=str(uuid.uuid4()))


async def _run(args) -> None:
    if not args.phone_number:
        logger.error("At least one --phone-number is required for outbound direction.")
        sys.exit(1)

    instructions = open(args.instructions_path, encoding="utf-8").read()

    try:
        call_orchestrator = CallOrchestrator(
            instructions=[instructions],
            phone_numbers=args.phone_number,
            concurrency=args.concurrency,
            rounds=args.rounds,
            concurrent_tasks_runner=ConcurrentTasksRunner(
                logger=create_logger(name="ConcurrentTasksRunner"),
            ),
            logger=create_logger(name="CallOrchestrator"),
        )
        await call_orchestrator.run()
        logger.info("Successfully ran.")
        sys.exit(0)
    except Exception as e:
        logger.error("Failed to run.", extra={"error": str(e)})
        sys.exit(1)


def run(args) -> None:
    asyncio.run(_run(args))
