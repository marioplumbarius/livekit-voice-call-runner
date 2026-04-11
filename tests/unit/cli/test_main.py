import sys

import pytest

from livekit_voice_call_runner.cli.main import run


@pytest.mark.parametrize(
    "direction, mock_target",
    [
        ("outbound", "livekit_voice_call_runner.cli.main.run_outbound"),
        ("inbound", "livekit_voice_call_runner.cli.main.run_inbound"),
    ],
)
def test_run_when_direction_is_valid(mocker, tmp_path, direction, mock_target):
    instructions_file = tmp_path / "instructions.md"
    instructions_file.write_text("Test instructions")

    mock_run = mocker.patch(mock_target)
    argv = [
        "livekit_voice_call_runner",
        "--direction",
        direction,
        "--instructions-path",
        str(instructions_file),
    ]
    if direction == "outbound":
        argv += ["--phone-number", "+1234567890"]

    sys.argv = argv
    run()

    mock_run.assert_called_once()


@pytest.mark.parametrize(
    "argv",
    [
        ["livekit_voice_call_runner", "--instructions-path", "some/path.md"],
        ["livekit_voice_call_runner", "--direction", "sideways", "--instructions-path", "some/path.md"],
    ],
)
def test_run_when_direction_is_invalid(argv):
    sys.argv = argv
    with pytest.raises(SystemExit):
        run()


@pytest.mark.parametrize(
    "argv",
    [
        ["livekit_voice_call_runner", "--direction", "inbound"],
        ["livekit_voice_call_runner", "--direction", "outbound", "--instructions-path", "some/path.md"],
    ],
)
def test_run_when_required_arg_is_missing(argv):
    sys.argv = argv
    with pytest.raises(SystemExit):
        run()
