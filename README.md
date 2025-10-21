# livekit-voice-call-runner
Under Construction...

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
```bash
poetry run livekit_voice_call_runner \
    --phone-number +1234567890 \
    --instructions-path examples/instructions/discuss_car_issue.md \
    --rounds 1 \
    --concurrency 1
```
