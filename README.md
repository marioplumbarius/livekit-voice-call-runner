# livekit-voice-call-runner

A LiveKit-powered voice call runner that supports both **outbound** (dial-out) and **inbound** (listen for incoming) call directions, driven by a configurable AI agent.

## Prerequisites

- Python 3.10.18
- Poetry 2.1.3+
- LiveKit
- Azure OpenAI

## Setup

```bash
cp .env.template .env # hint: update placeholders
poetry install --with dev
poetry config virtualenvs.in-project true
poetry run pre-commit install
```

## Run it

### Outbound — dial out to one or more phone numbers

```bash
poetry run livekit_voice_call_runner \
    --direction outbound \
    --phone-number +1234567890 \
    --instructions-path examples/instructions/discuss_car_issue.md \
    --rounds 1 \
    --concurrency 1
```

### Inbound — listen for incoming calls

```bash
poetry run livekit_voice_call_runner \
    --direction inbound \
    --instructions-path examples/instructions/answer_service_call.md
```

## CLI flags

| Flag | Required | Description |
|---|---|---|
| `--direction` | yes | `outbound` or `inbound` |
| `--instructions-path` | yes | Path to the agent instructions file |
| `--phone-number` | outbound only | Phone number(s) to dial (repeatable) |
| `--rounds` | outbound only | Number of rounds to run (default: 1) |
| `--concurrency` | outbound only | Concurrent scenarios per round (default: 1) |
