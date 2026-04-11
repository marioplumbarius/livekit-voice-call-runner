import argparse

from livekit_voice_call_runner.cli import outbound


def run() -> None:
    parser = argparse.ArgumentParser(prog="livekit_voice_call_runner")
    parser.add_argument(
        "--instructions-path",
        required=True,
        help="Path to the file containing the instructions for the call agent.",
    )
    parser.add_argument(
        "--phone-number",
        action="append",
        required=True,
        help="Phone number to call (can be specified multiple times).",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=1,
        help="Number of rounds to run the scenarios.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Number of scenarios to run concurrently.",
    )
    args = parser.parse_args()
    outbound.run(args)
