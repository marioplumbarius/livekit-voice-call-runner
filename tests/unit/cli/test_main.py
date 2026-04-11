import sys

import pytest

from livekit_voice_call_runner.cli.main import run


def test_run_dispatches_to_outbound(mocker, tmp_path):
    instructions_file = tmp_path / "instructions.md"
    instructions_file.write_text("Test instructions")

    mock_run = mocker.patch("livekit_voice_call_runner.cli.outbound.run")
    sys.argv = [
        "livekit_voice_call_runner",
        "--instructions-path",
        str(instructions_file),
        "--phone-number",
        "+1234567890",
    ]
    run()

    mock_run.assert_called_once()


@pytest.mark.parametrize(
    "argv",
    [
        ["livekit_voice_call_runner"],
        ["livekit_voice_call_runner", "--instructions-path", "some/path.md"],
    ],
)
def test_run_when_required_args_missing(argv):
    sys.argv = argv
    with pytest.raises(SystemExit):
        run()
