from functools import partial
import sys

from livekit.agents import cli
from livekit.agents.worker import WorkerOptions
from livekit_voice_call_runner.inbound import worker


def run(args) -> None:
    instructions = open(args.instructions_path, encoding="utf-8").read()
    # Force the LiveKit agents worker into dev mode, bypassing the livekit CLI sub-command requirement.
    sys.argv = [sys.argv[0], "dev"]
    cli.run_app(opts=WorkerOptions(entrypoint_fnc=partial(worker.handle, instructions=instructions)))
