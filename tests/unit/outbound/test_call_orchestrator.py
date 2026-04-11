from unittest.mock import AsyncMock, MagicMock

import pytest

from livekit_voice_call_runner.concurrency.tasks_runner import ConcurrentTasksRunner
from livekit_voice_call_runner.logger import create_logger
from livekit_voice_call_runner.outbound.call_orchestrator import OutboundCallOrchestrator


@pytest.fixture
def mock_concurrent_runner():
    runner = MagicMock(spec=ConcurrentTasksRunner)
    runner.run = AsyncMock()
    return runner


@pytest.fixture
def mock_cfg():
    return MagicMock()


@pytest.fixture
def mock_outbound_cfg():
    return MagicMock()


@pytest.fixture
def mock_livekit_api():
    return MagicMock()


@pytest.fixture
def orchestrator(mock_concurrent_runner, mock_cfg, mock_outbound_cfg, mock_livekit_api):
    return OutboundCallOrchestrator(
        instructions=["Do task A."],
        phone_numbers=["+1111111111", "+2222222222"],
        concurrency=2,
        rounds=1,
        concurrent_tasks_runner=mock_concurrent_runner,
        logger=create_logger(name="test-orchestrator"),
        cfg=mock_cfg,
        outbound_cfg=mock_outbound_cfg,
        livekit_api=mock_livekit_api,
    )


async def test_build_props_creates_cartesian_product(orchestrator, mocker):
    mock_props = MagicMock()
    mocker.patch(
        "livekit_voice_call_runner.factory.create_call_runner_props",
        return_value=mock_props,
    )

    props = orchestrator._build_call_runner_props()

    # 1 instruction × 2 phone numbers = 2 props; padded to concurrency (2)
    assert len(props) == 2


async def test_run_executes_correct_number_of_rounds(orchestrator, mocker):
    orchestrator._rounds = 3
    mock_run_round = mocker.patch.object(orchestrator, "_run_round", new_callable=AsyncMock)

    await orchestrator.run()

    assert mock_run_round.call_count == 3


async def test_run_round_submits_tasks_to_concurrent_runner(orchestrator, mocker):
    mock_props = MagicMock()
    mock_props.model_config = {"arbitrary_types_allowed": True}
    mocker.patch.object(orchestrator, "_build_call_runner_props", return_value=[mock_props])
    mocker.patch("livekit_voice_call_runner.outbound.call_orchestrator.OutboundCallRunner")

    await orchestrator._run_round(round=0)

    orchestrator._concurrent_tasks_runner.run.assert_called_once()
    call_kwargs = orchestrator._concurrent_tasks_runner.run.call_args.kwargs
    assert call_kwargs["concurrency"] == orchestrator._concurrency
