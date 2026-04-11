# HLD: Refactor outbound + config (mario/refactor-outbound-config)

## Goal

Split the original monolithic PR #1 into two reviewable units. This first PR restructures the
existing outbound-only codebase without adding new user-facing features.

## Problem

- `cli.py`, `config.py`, `core/factory.py`, and all dialer/runner files live in a flat
  structure that does not scale when a second call direction (inbound) is added.
- `config.py` is eagerly evaluated at import time, making unit tests fragile.
- Outbound helpers (`call_dialer`, `call_orchestrator`, `call_room_connector`, `call_runner`)
  are mixed into `core/` alongside shared primitives.
- `is_set()` is missing from a shutdown guard in `core/call_session_starter.py`.

## Solution

Reorganise the module layout and fix the bug. No new user-visible behaviour.

### Module changes

| Before | After | Notes |
|---|---|---|
| `cli.py` | `cli/main.py` + `cli/outbound.py` | same CLI flags |
| `config.py` | `config/base.py` + `config/outbound.py` | lazy `lru_cache` |
| `core/factory.py` | `factory.py` | promoted to package root |
| `core/call_dialer.py` | `outbound/call_dialer.py` | move only |
| `core/call_orchestrator.py` | `outbound/call_orchestrator.py` | rename class + imports |
| `core/call_room_connector.py` | `outbound/call_room_connector.py` | move only |
| `core/call_runner.py` | `outbound/call_runner.py` | update imports |

### Bug fixes

- `core/call_session_starter.py`: `if not self._shutdown:` → `if not self._shutdown.is_set():`
- `core/call_event_listener.py` + `core/call_session_starter.py`: widen `CallRoom` parameter
  type to `rtc.Room` so the same helpers work for inbound rooms (preparation for PR 2).

### Config

- `config/base.py`: shared env vars (LLM, LiveKit base, room, session). Lazy via `@lru_cache`.
- `config/outbound.py`: outbound-only vars (`LIVEKIT_OUTBOUND_SIP_TRUNK_ID`, dialer settings).
  Lazy via `@lru_cache`.
- `.env.template`: sectioned with `(base)` / `(outbound)` labels.

### Tests

- New `tests/` tree with `conftest.py`.
- `asyncio_mode = "auto"` added to `pyproject.toml` for `pytest-asyncio`.
- Covers: config (base + outbound), core (event listener + session starter), outbound
  (orchestrator + runner), CLI (main + outbound dispatch).

## Tasks

- [x] Delete `cli.py`; add `cli/__init__.py`, `cli/main.py`, `cli/outbound.py`
- [x] Delete `config.py`; add `config/__init__.py`, `config/base.py`, `config/outbound.py`
- [x] Move `core/factory.py` → `factory.py`; update import sites
- [x] Move `call_dialer/orchestrator/room_connector/runner` from `core/` → `outbound/`
- [x] Fix `is_set()` bug; widen `CallRoom` → `rtc.Room`
- [x] Update `pyproject.toml` entry point + `asyncio_mode`; restructure `.env.template`
- [x] Add tests

## Deviations

_None yet._
