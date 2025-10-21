import argparse
import asyncio
import sys
import uuid
from pathlib import Path

from pydantic import BaseModel

from livekit_voice_call_runner.concurrency.tasks_runner import ConcurrentTasksRunner
from livekit_voice_call_runner.core.call_orchestrator import CallOrchestrator
from livekit_voice_call_runner.logger import create_logger

logger = create_logger(name=__name__, correlation_id=str(uuid.uuid4()))


class CLIArguments(BaseModel):
    concurrency: int
    instructions: list[str]
    phone_numbers: list[str]
    rounds: int


class CLIParser:
    def __init__(self):
        self._parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--instructions-path",
            help="Path to the file containing the instructions for the call agent.",
            type=str,
            action="append",
            required=True,
        )
        parser.add_argument(
            "--phone-number",
            help="Phone number to call.",
            type=str,
            action="append",
            required=True,
        )
        parser.add_argument(
            "--concurrency",
            help="Number of scenarios to run concurrently",
            type=int,
            default=1,
        )
        parser.add_argument(
            "--rounds",
            help="Number of rounds to run the scenarios",
            type=int,
            default=1,
        )
        return parser

    def parse_arguments(self) -> CLIArguments:
        parsed_args = self._parser.parse_args()

        return CLIArguments(
            concurrency=parsed_args.concurrency,
            instructions=[
                Path(p).read_text(
                    encoding="utf-8",
                )
                for p in parsed_args.instructions_path
            ],
            phone_numbers=parsed_args.phone_number,
            rounds=parsed_args.rounds,
        )


async def _run():
    arguments = CLIParser().parse_arguments()

    try:
        call_orchestrator = CallOrchestrator(
            instructions=arguments.instructions,
            phone_numbers=arguments.phone_numbers,
            concurrency=arguments.concurrency,
            rounds=arguments.rounds,
            concurrent_tasks_runner=ConcurrentTasksRunner(
                logger=create_logger(name=ConcurrentTasksRunner.__name__),
            ),
            logger=create_logger(name=CallOrchestrator.__name__),
        )
        await call_orchestrator.run()
        logger.info("Successfully ran tests.")
        sys.exit(0)
    except Exception as e:
        logger.error("Failed to run tests.", extra={"error": str(e)})
        sys.exit(1)


def run():
    asyncio.run(_run())
