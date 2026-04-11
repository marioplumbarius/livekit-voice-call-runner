import argparse

import pytest

from livekit_voice_call_runner.cli.inbound import run


def test_run_reads_instructions_and_calls_worker_run(mocker, tmp_path):
    instructions_content = "You are a helpful assistant."
    instructions_file = tmp_path / "instructions.md"
    instructions_file.write_text(instructions_content)

    mock_run = mocker.patch("livekit_voice_call_runner.inbound.worker.run")

    args = argparse.Namespace(instructions_path=str(instructions_file))
    run(args)

    mock_run.assert_called_once_with(instructions=instructions_content)


def test_run_raises_if_instructions_file_missing(tmp_path):
    args = argparse.Namespace(instructions_path=str(tmp_path / "nonexistent.md"))

    with pytest.raises(FileNotFoundError):
        run(args)
