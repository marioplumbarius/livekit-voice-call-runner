import argparse

import pytest

from livekit_voice_call_runner.cli.outbound import run


def test_run_calls_orchestrator(mocker, tmp_path):
    instructions_content = "Call instructions"
    instructions_file = tmp_path / "instructions.md"
    instructions_file.write_text(instructions_content)

    # autospec=True ensures __name__ is properly resolved from the real class
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
    call_kwargs = mock_orchestrator_cls.call_args.kwargs
    assert call_kwargs["instructions"] == [instructions_content]
    assert call_kwargs["phone_numbers"] == ["+1234567890"]
    assert call_kwargs["concurrency"] == 1
    assert call_kwargs["rounds"] == 1
