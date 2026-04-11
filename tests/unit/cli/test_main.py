import sys

import pytest

from livekit_voice_call_runner.cli.main import run


@pytest.mark.parametrize(
    "argv_extra, mock_target",
    [
        (
            ["--direction", "outbound", "--phone-number", "+1234567890"],
            "livekit_voice_call_runner.cli.outbound.run",
        ),
        (
            ["--direction", "inbound"],
            "livekit_voice_call_runner.cli.inbound.run",
        ),
    ],
)
def test_run_when_direction_is_valid(mocker, tmp_path, argv_extra, mock_target):
    instructions_file = tmp_path / "instructions.md"
    instructions_file.write_text("Test instructions")

    mock_run = mocker.patch(mock_target)
    sys.argv = [
        "livekit_voice_call_runner",
        "--instructions-path",
        str(instructions_file),
    ] + argv_extra
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


def test_run_when_instructions_path_not_found():
    sys.argv = ["livekit_voice_call_runner", "--direction", "inbound"]
    with pytest.raises(SystemExit):
        run()


def test_run_when_no_phone_number():
    sys.argv = [
        "livekit_voice_call_runner",
        "--direction",
        "outbound",
        "--instructions-path",
        "some/path.md",
    ]
    with pytest.raises(SystemExit):
        run()
