import itertools
import uuid

from livekit import api

from livekit_voice_call_runner import factory
from livekit_voice_call_runner.concurrency.tasks_runner import ConcurrentTasksRunner
from livekit_voice_call_runner.config.outbound import OutboundConfig
from livekit_voice_call_runner.config.shared import Config
from livekit_voice_call_runner.logger import CallLogger
from livekit_voice_call_runner.outbound.call_runner import OutboundCallRunner, OutboundCallRunnerProps


class OutboundCallOrchestrator:
    def __init__(
        self,
        instructions: list[str],
        phone_numbers: list[str],
        concurrency: int,
        rounds: int,
        concurrent_tasks_runner: ConcurrentTasksRunner,
        logger: CallLogger,
        cfg: Config,
        outbound_cfg: OutboundConfig,
        livekit_api: api.LiveKitAPI,
    ):
        self._instructions = instructions
        self._phone_numbers = phone_numbers
        self._concurrency = concurrency
        self._rounds = rounds
        self._concurrent_tasks_runner = concurrent_tasks_runner
        self._logger = logger
        self._cfg = cfg
        self._outbound_cfg = outbound_cfg
        self._livekit_api = livekit_api

    def _build_call_runner_props(self) -> list[OutboundCallRunnerProps]:
        props = [
            factory.create_call_runner_props(
                instructions=instructions,
                phone_number_to=to_phone_number,
                correlation_id=str(uuid.uuid4()),
                cfg=self._cfg,
                outbound_cfg=self._outbound_cfg,
                livekit_api=self._livekit_api,
            )
            for instructions in self._instructions
            for to_phone_number in self._phone_numbers
        ]

        # repeat the inputs to reach max concurrency
        min_size = max(len(props), self._concurrency)
        return list(itertools.islice(itertools.cycle(props), min_size))

    async def _run_round(self, round: int) -> None:
        logger_extra = {"round": round, "concurrency": self._concurrency}
        self._logger.info("Running round.", extra=logger_extra)

        props = self._build_call_runner_props()
        tasks = [OutboundCallRunner(props=prop).run() for prop in props]
        await self._concurrent_tasks_runner.run(tasks=tasks, concurrency=self._concurrency)

        self._logger.info("Successfully ran round.", extra=logger_extra)

    async def run(self) -> None:
        self._logger.info(
            "Running rounds.",
            extra={"count": self._rounds, "concurrency": self._concurrency},
        )

        for round in range(self._rounds):
            await self._run_round(round=round)

        self._logger.info("Successfully ran rounds.")
