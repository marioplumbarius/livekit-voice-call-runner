# HLD: Add inbound call agent (mario/add-inbound)

## Goal

Add inbound call support (LiveKit Agents worker dispatch) on top of the refactored outbound
base from `mario/refactor-outbound-config`.

## Problem

The project can only make outbound SIP calls. Service teams also need to receive inbound calls
routed through LiveKit's dispatch mechanism.

## Solution

Introduce a `--direction outbound|inbound` CLI flag. When `inbound` is selected, a LiveKit
Agents worker starts in dev mode, waiting for room-dispatch events.

### New modules

- **`inbound/worker.py`**: `_make_entrypoint(instructions)` returns an `async def entrypoint(ctx)`
  closure that connects to the room, creates the call agent and session, and waits for shutdown.
  `run(instructions)` forces `sys.argv = [argv[0], "dev"]` and calls `cli.run_app`.
- **`cli/inbound.py`**: reads `args.instructions_path` and delegates to `worker.run`.
- **`core/call_agent.py`**: class stays as `CallAgent` — it is used by both directions.

### Modified modules

- **`cli/main.py`**: add `--direction outbound|inbound` (required enum), make `--phone-number`
  optional (required only for outbound), dispatch to `outbound.run` or `inbound.run`.
- **`factory.py`**: add `create_call_agent`, `create_call_session_starter`, and
  `create_call_event_listener` public helpers consumed by `inbound/worker.py`.
- **`core/call_event_listener.py`** + **`core/call_session_starter.py`**: no agent rename needed.
- **`outbound/call_runner.py`**: no agent rename needed.

### New files

- `examples/instructions/answer_service_call.md`

### Tests

- `tests/unit/inbound/test_worker.py`
- `tests/unit/cli/test_inbound.py`
- `tests/unit/cli/test_main.py` extended with both-direction dispatch cases

## Tasks

- [x] Keep `CallAgent` name (used by both directions); add `create_call_agent` factory helper
- [x] Add `inbound/__init__.py`, `inbound/worker.py`, `cli/inbound.py`
- [x] Update `cli/main.py` with `--direction` dispatch
- [x] Add inbound helpers to `factory.py`
- [x] Add `examples/instructions/answer_service_call.md`
- [x] Add inbound tests; extend `test_main.py`

## Deviations

- Originally planned to rename `CallAgent` → `InboundCallAgent`. Reverted per review feedback:
  the class is used by both outbound and inbound, so `CallAgent` is the correct name.
  Consequently, the factory function was named `create_call_agent` (not `create_inbound_call_agent`).
