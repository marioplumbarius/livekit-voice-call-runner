import pytest


class TestInboundCLI:
    def test_run_reads_instructions_and_calls_run_worker(self, mocker, tmp_path):
        instructions_content = "You are a helpful assistant."
        instructions_file = tmp_path / "instructions.md"
        instructions_file.write_text(instructions_content)

        mock_run_worker = mocker.patch("livekit_voice_call_runner.inbound.worker.run_worker")

        import argparse

        args = argparse.Namespace(instructions_path=str(instructions_file))

        from livekit_voice_call_runner.cli.inbound import run

        run(args)

        mock_run_worker.assert_called_once_with(instructions=instructions_content)

    def test_run_raises_if_instructions_file_missing(self, tmp_path):
        import argparse

        args = argparse.Namespace(instructions_path=str(tmp_path / "nonexistent.md"))

        from livekit_voice_call_runner.cli.inbound import run

        with pytest.raises(FileNotFoundError):
            run(args)
