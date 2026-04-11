import argparse

import pytest

from livekit_voice_call_runner.cli.inbound import run


def test_run_successfully(mocker, tmp_path):
    instructions_content = "You are a helpful assistant."
    # tmp_path is a pytest fixture that creates a temporary directory cleaned up after the test.
    instructions_file = tmp_path / "instructions.md"
    instructions_file.write_text(instructions_content)

    mock_run = mocker.patch("livekit_voice_call_runner.inbound.worker.run")

    args = argparse.Namespace(instructions_path=str(instructions_file))
    run(args)

    mock_run.assert_called_once_with(instructions=instructions_content)


def test_run_when_instructions_path_not_found(tmp_path):
    args = argparse.Namespace(instructions_path=str(tmp_path / "nonexistent.md"))

    with pytest.raises(FileNotFoundError):
        run(args)
