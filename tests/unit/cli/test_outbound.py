import argparse

import pytest

from livekit_voice_call_runner.cli.outbound import run


def test_run(mocker, tmp_path):
    instructions_content = "Call instructions"
    instructions_file = tmp_path / "instructions.md"
    instructions_file.write_text(instructions_content)

    mock_orchestrator_cls = mocker.patch(
        "livekit_voice_call_runner.cli.outbound.OutboundCallOrchestrator",
        autospec=True,
    )

    args = argparse.Namespace(
        instructions_path=str(instructions_file),
        phone_number=["+1234567890"],
        concurrency=1,
        rounds=1,
    )

    with pytest.raises(SystemExit) as exc_info:
        run(args)

    assert exc_info.value.code == 0
    mock_orchestrator_cls.assert_called_once()
    mock_orchestrator_cls.return_value.run.assert_called_once()
