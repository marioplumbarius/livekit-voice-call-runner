from livekit_voice_call_runner.inbound import worker


def run(args) -> None:
    instructions = open(args.instructions_path, encoding="utf-8").read()
    worker.run(instructions=instructions)
