from livekit_voice_call_runner.inbound.worker import run_worker


def run(args) -> None:
    instructions = open(args.instructions_path, encoding="utf-8").read()
    run_worker(instructions=instructions)
