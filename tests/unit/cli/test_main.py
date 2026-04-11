import sys

import pytest


class TestCLIDispatcher:
    def test_outbound_direction_calls_outbound_run(self, mocker, tmp_path):
        instructions_file = tmp_path / "instructions.md"
        instructions_file.write_text("Test instructions")

        mock_run = mocker.patch("livekit_voice_call_runner.cli.outbound.run")
        sys.argv = [
            "livekit_voice_call_runner",
            "--direction",
            "outbound",
            "--instructions-path",
            str(instructions_file),
            "--phone-number",
            "+1234567890",
        ]
        from livekit_voice_call_runner.cli.main import run

        run()
        mock_run.assert_called_once()

    def test_inbound_direction_calls_inbound_run(self, mocker, tmp_path):
        instructions_file = tmp_path / "instructions.md"
        instructions_file.write_text("Test instructions")

        mock_run = mocker.patch("livekit_voice_call_runner.cli.inbound.run")
        sys.argv = [
            "livekit_voice_call_runner",
            "--direction",
            "inbound",
            "--instructions-path",
            str(instructions_file),
        ]
        from livekit_voice_call_runner.cli.main import run

        run()
        mock_run.assert_called_once()

    def test_missing_direction_exits(self, tmp_path):
        instructions_file = tmp_path / "instructions.md"
        instructions_file.write_text("Test instructions")

        sys.argv = [
            "livekit_voice_call_runner",
            "--instructions-path",
            str(instructions_file),
        ]
        from livekit_voice_call_runner.cli.main import run

        with pytest.raises(SystemExit):
            run()

    def test_invalid_direction_exits(self, tmp_path):
        instructions_file = tmp_path / "instructions.md"
        instructions_file.write_text("Test instructions")

        sys.argv = [
            "livekit_voice_call_runner",
            "--direction",
            "sideways",
            "--instructions-path",
            str(instructions_file),
        ]
        from livekit_voice_call_runner.cli.main import run

        with pytest.raises(SystemExit):
            run()

    def test_missing_instructions_path_exits(self):
        sys.argv = ["livekit_voice_call_runner", "--direction", "inbound"]
        from livekit_voice_call_runner.cli.main import run

        with pytest.raises(SystemExit):
            run()
